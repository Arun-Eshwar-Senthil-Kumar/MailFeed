"""Generic IMAP client — works with any provider that offers IMAP + app passwords."""
import imaplib, email, re
from email.header import decode_header, make_header
from email.utils import parseaddr, parsedate_to_datetime

HOSTS = {"gmail.com": "imap.gmail.com", "googlemail.com": "imap.gmail.com",
         "yahoo.com": "imap.mail.yahoo.com", "ymail.com": "imap.mail.yahoo.com",
         "icloud.com": "imap.mail.me.com", "me.com": "imap.mail.me.com",
         "outlook.com": "outlook.office365.com", "hotmail.com": "outlook.office365.com",
         "live.com": "outlook.office365.com", "zoho.com": "imap.zoho.com",
         "aol.com": "imap.aol.com", "gmx.com": "imap.gmx.com"}

def host_for(addr: str, custom: str | None = None) -> str:
    dom = addr.split("@")[-1].strip().lower()
    return (custom or "").strip() or HOSTS.get(dom) or f"imap.{dom}"

def _dec(v): return str(make_header(decode_header(v or "")))

def _body(msg) -> str:
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "ignore")
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", "ignore")
            return re.sub(r"<[^>]+>", " ", html)
    return ""

def _conn(c):
    m = imaplib.IMAP4_SSL(c["host"], timeout=25)
    m.login(c["email"], c["password"])
    return m

def check(c):
    _conn(c).logout()

def fetch_recent(c, limit=30, skip=frozenset()):
    """Returns (all_uids_in_window, new_messages). Messages in `skip` aren't downloaded again."""
    m = _conn(c); m.select("INBOX", readonly=True)
    _, data = m.uid("search", None, "ALL")
    uids = [u.decode() for u in data[0].split()[-limit:]]
    new = []
    for uid in uids:
        if uid in skip: continue
        _, d = m.uid("fetch", uid, "(BODY.PEEK[]<0.60000>)")  # first 60 KB only: skips big attachments
        msg = email.message_from_bytes(d[0][1])
        name, addr = parseaddr(msg["From"])
        try: ts = parsedate_to_datetime(msg["Date"]).timestamp()
        except Exception: ts = 0
        new.append({"id": uid, "sender_name": _dec(name), "sender_email": addr,
                    "subject": _dec(msg["Subject"]), "body": _body(msg), "timestamp": ts})
    m.logout()
    return uids, new

def _find_folder(m, flag, names):
    _, lines = m.list()
    for l in lines or []:
        s = l.decode(errors="ignore")
        mt = re.search(r'\)\s+(?:"[^"]*"|NIL)\s+(.+)$', s)
        if mt and (flag in s or mt.group(1).strip('"').lower() in names):
            return mt.group(1).strip('"')
    return None

def _move(c, uid, gmail_op, flag, names):
    m = _conn(c); m.select("INBOX")
    if c["host"] == "imap.gmail.com":
        m.uid("store", uid, *gmail_op)
    else:
        folder = _find_folder(m, flag, names)
        if not folder: raise RuntimeError("Couldn't find the target folder on this mail server")
        m.uid("copy", uid, f'"{folder}"'); m.uid("store", uid, "+FLAGS", "\\Deleted"); m.expunge()
    m.logout()

def archive(c, uid): _move(c, uid, ("-X-GM-LABELS", "\\Inbox"), "\\Archive", {"archive", "archived", "all mail"})
def trash(c, uid):   _move(c, uid, ("+X-GM-LABELS", "\\Trash"), "\\Trash", {"trash", "deleted items", "deleted messages", "bin"})