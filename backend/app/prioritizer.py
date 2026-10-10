import re
from datetime import datetime, timezone

P1 = re.compile(r"\b(internship|intern\b|job|application|applied|interview|shortlist(ed)?|"
                r"offer letter|recruit\w*|hiring|candidate|candidacy|online assessment|"
                r"coding test|career|vacancy|position)\b", re.I)
P2 = re.compile(r"\b(deadline|due|submission|submit|assignment|project|registration|"
                r"register|exam|viva|lab report|last date|closes on)\b", re.I)

def classify(subject: str, body: str) -> int:
    """1 = job/internship, 2 = deadlines/academics, 3 = everything else.
    Subject is weighted: a subject hit wins; body-only hits need 2+ matches (cuts false positives)."""
    if P1.search(subject) or len(P1.findall(body[:2000])) >= 2: return 1
    if P2.search(subject) or len(P2.findall(body[:2000])) >= 2: return 2
    return 3

def urgency(events: list[dict]) -> float:
    """0..1 — higher the sooner the nearest upcoming event is."""
    now = datetime.now(timezone.utc)
    hrs = [(datetime.fromisoformat(e["start"]) - now).total_seconds() / 3600 for e in events]
    hrs = [h for h in hrs if h >= 0]
    return 0.0 if not hrs else 1 / (1 + min(hrs) / 24)

def sort_feed(items: list[dict]) -> list[dict]:
    # priority asc, then urgency desc, then newest first
    return sorted(items, key=lambda i: (i["priority"], -i["urgency"], -i["timestamp"]))
