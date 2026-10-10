from dotenv import load_dotenv; load_dotenv()
import secrets, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from . import mail_client as mail
from .filters import is_blocked
from .prioritizer import classify, urgency, sort_feed
from .extractor import extract_events
from .summarizer import summarize
from .hooks import hook

app = FastAPI(title="MailFeed")
SESSIONS: dict[str, dict] = {}   # token -> {creds, cache, out, ts}  (in memory only; cleared on restart)
POOL = ThreadPoolExecutor(8)

class Login(BaseModel):
    email: str
    password: str
    host: str | None = None

def _why(e: Exception) -> str:
    s = str(e)
    if any(k in s.lower() for k in ("authenticationfailed", "application-specific", "invalid credentials", "login failed", "authenticate")):
        return "Login failed. Use an app password (not your normal password) and make sure IMAP is enabled."
    if isinstance(e, OSError):
        return "Couldn't reach the mail server. Check the address, or set the IMAP server under Advanced."
    return s[:200]

def sess(request: Request) -> dict:
    s = SESSIONS.get(request.cookies.get("sid", ""))
    if not s: raise HTTPException(401, "Not signed in")
    return s

@app.post("/login")
def login(b: Login, resp: Response):
    c = {"email": b.email.strip(), "password": b.password.replace(" ", ""), "host": mail.host_for(b.email, b.host)}
    try: mail.check(c)
    except Exception as e: raise HTTPException(401, _why(e))
    tok = secrets.token_urlsafe(32)
    SESSIONS[tok] = {"creds": c, "cache": {}, "out": None, "ts": 0}
    resp.set_cookie("sid", tok, httponly=True, samesite="lax", max_age=60 * 60 * 12)
    return {"email": c["email"]}

@app.post("/logout")
def logout(request: Request, resp: Response):
    SESSIONS.pop(request.cookies.get("sid", ""), None); resp.delete_cookie("sid"); return {"ok": True}

@app.get("/me")
def me(s=Depends(sess)): return {"email": s["creds"]["email"]}

def _build(e):
    # Rule: "student welfare" mail is hidden completely (sender name, address or subject)
    if is_blocked(e["sender_name"], e["sender_email"], e["subject"]): return e["id"], None
    pr = classify(e["subject"], e["body"])
    return e["id"], {"id": e["id"], "sender": e["sender_name"] or e["sender_email"], "subject": e["subject"],
                     "summary": summarize(e["subject"], e["body"]), "priority": pr,
                     "hook": hook(e["subject"], e["body"], pr), "timestamp": e["timestamp"],
                     "events": extract_events(e["subject"], e["body"])}

@app.get("/feed")
def feed(limit: int = 20, s=Depends(sess)):
    if s["out"] and time.time() - s["ts"] < 45: return s["out"]
    try: uids, new = mail.fetch_recent(s["creds"], limit, set(s["cache"]))
    except Exception as e: raise HTTPException(502, _why(e))
    for uid, item in POOL.map(_build, new): s["cache"][uid] = item
    items = [s["cache"][u] for u in uids if s["cache"].get(u)]
    for i in items: i["urgency"] = urgency(i["events"])
    items = sort_feed(items)
    s["out"] = {"stories": [i for i in items if i["priority"] == 1][:10], "feed": items}; s["ts"] = time.time()
    return s["out"]

def _act(s, uid, fn):
    try: fn(s["creds"], uid)
    except Exception as e: raise HTTPException(502, _why(e))
    s["cache"].pop(uid, None); s["out"] = None
    return {"ok": True}

@app.post("/emails/{uid}/archive")
def archive(uid: str, s=Depends(sess)): return _act(s, uid, mail.archive)

@app.delete("/emails/{uid}")
def delete(uid: str, s=Depends(sess)): return _act(s, uid, mail.trash)

_STATIC = Path(__file__).resolve().parent.parent / "static"

@app.get("/", include_in_schema=False)
def home(): return FileResponse(_STATIC / "index.html")