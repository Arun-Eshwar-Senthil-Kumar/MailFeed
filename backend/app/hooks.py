import re
# (pattern, icon, short catchy label) — first match wins, most specific first
RULES = [
    (r"interview", "🎯", "Interview update"),
    (r"offer letter|job offer|offer of employment|selected for|congratulations on", "🎉", "Offer alert"),
    (r"shortlist", "⭐", "You're shortlisted"),
    (r"internship|\bintern\b", "🚀", "Internship chance"),
    (r"application|applied|candidate|candidacy", "💼", "Application update"),
    (r"\bjob\b|hiring|vacancy|recruit|career|position", "💼", "Job alert"),
    (r"assignment|submission|submit", "📚", "Submission due"),
    (r"deadline|\bdue\b|last date|closes on", "⏰", "Deadline coming"),
    (r"regist|rsvp|sign.?up", "📝", "Registration open"),
    (r"\bexam\b|viva", "🧠", "Exam notice"),
]

def hook(subject: str, body: str, priority: int) -> dict:
    texts = (subject,) if priority == 3 else (subject, body[:800])
    for t in texts:
        for pat, icon, label in RULES:
            if re.search(pat, t, re.I): return {"icon": icon, "label": label}
    return {"icon": "📬", "label": "New email"}
