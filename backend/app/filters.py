import re

# Matches "student welfare", "student-welfare", "studentwelfare", "student_welfare"
_BLOCK = re.compile(r"student[\s_.\-]*welfare", re.I)

def is_blocked(sender_name: str, sender_email: str, subject: str) -> bool:
    """True if the email must be hidden (checks name, address and subject)."""
    return any(_BLOCK.search(f or "") for f in (sender_name, sender_email, subject))
