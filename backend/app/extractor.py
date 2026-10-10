import re
from datetime import datetime, timedelta, timezone
import dateparser
from dateparser.search import search_dates

URL = re.compile(r"https?://[^\s<>\"')]+")
REG_HINT = re.compile(r"regist|apply|rsvp|sign.?up|join|form|forms\.gle|eventbrite|luma", re.I)
_SETTINGS = {"PREFER_DATES_FROM": "future", "RETURN_AS_TIMEZONE_AWARE": True,
             "TIMEZONE": "Asia/Kolkata", "TO_TIMEZONE": "UTC"}
_HAS_DIGIT = re.compile(r"\d")

def registration_link(text: str) -> str | None:
    urls = [u.rstrip(".,;") for u in URL.findall(text)]
    return next((u for u in urls if REG_HINT.search(u)), None) or (urls[0] if urls else None)

def extract_events(subject: str, body: str) -> list[dict]:
    """Find future dates/times in the email -> calendar-ready events (ISO UTC)."""
    now = datetime.now(timezone.utc)
    link = registration_link(body)
    found = search_dates(body[:2000], languages=["en"], settings=_SETTINGS) or []
    events, seen = [], set()
    for phrase, dt in found:
        # skip fuzzy hits like "may", "today", "one" — require a digit in the phrase
        if not _HAS_DIGIT.search(phrase) or dt <= now or dt in seen: continue
        seen.add(dt)
        # date-only (midnight local) -> treat as an all-day-ish 9:00 reminder
        local_midnight = dateparser.parse(phrase, settings={**_SETTINGS, "TO_TIMEZONE": "Asia/Kolkata"})
        if local_midnight and local_midnight.hour == 0 and local_midnight.minute == 0:
            dt = dt + timedelta(hours=9)
        events.append({"title": subject, "start": dt.isoformat(),
                       "end": (dt + timedelta(hours=1)).isoformat(),
                       "url": link, "source_phrase": phrase})
    return sorted(events, key=lambda e: e["start"])[:3]