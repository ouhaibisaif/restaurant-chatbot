from __future__ import annotations

import re
from datetime import date, datetime, timedelta


PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{5,}\d)")
PEOPLE_RE = re.compile(r"\b(?:for\s*)?([1-9]|[12][0-9]|30)\s*(?:people|persons|guests|pax|personnes|ناس|اشخاص)?\b", re.IGNORECASE)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/20\d{2})\b")
TIME_RE = re.compile(r"\b([01]?\d|2[0-3])[:h]([0-5]\d)\b|\b([1-9]|1[0-2])\s*(am|pm)\b", re.IGNORECASE)
NAME_RE = re.compile(r"(?:my name is|name is|i am|je m'appelle|mon nom est|اسمي)\s+([A-Za-zÀ-ÿ\u0600-\u06FF'’ -]{2,60})", re.IGNORECASE)


def parse_reservation_details(message: str) -> dict:
    details: dict = {}

    name_match = NAME_RE.search(message)
    if name_match:
        details["name"] = name_match.group(1).strip(" .,!؟")

    phone_match = PHONE_RE.search(message)
    if phone_match:
        details["phone"] = phone_match.group(1).strip()

    # Strip phone, date and time first so their digits aren't read as the party size.
    people_text = message
    for pattern in (PHONE_RE, DATE_RE, TIME_RE):
        people_text = pattern.sub(" ", people_text)
    people_match = PEOPLE_RE.search(people_text)
    if people_match:
        details["people"] = int(people_match.group(1))

    date_match = DATE_RE.search(message)
    if date_match:
        raw_date = date_match.group(1)
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                details["reservation_date"] = datetime.strptime(raw_date, fmt).date().isoformat()
                break
            except ValueError:
                continue
    elif re.search(r"\btomorrow\b", message, re.IGNORECASE):
        details["reservation_date"] = (date.today() + timedelta(days=1)).isoformat()
    elif re.search(r"\btoday\b", message, re.IGNORECASE):
        details["reservation_date"] = date.today().isoformat()

    time_match = TIME_RE.search(message)
    if time_match:
        if time_match.group(1) and time_match.group(2):
            details["reservation_time"] = f"{int(time_match.group(1)):02d}:{time_match.group(2)}"
        else:
            hour = int(time_match.group(3))
            meridiem = time_match.group(4).lower()
            if meridiem == "pm" and hour != 12:
                hour += 12
            if meridiem == "am" and hour == 12:
                hour = 0
            details["reservation_time"] = f"{hour:02d}:00"

    return details


def missing_reservation_fields(details: dict) -> list[str]:
    required = ["name", "phone", "reservation_date", "reservation_time", "people"]
    return [field for field in required if not details.get(field)]
