from datetime import date, timedelta
import re


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "sept": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "a": 1,
    "an": 1,
}


def _parse_number(s: str) -> int:
    s = s.strip().lower()
    if s.isdigit():
        return int(s)
    if s in NUMBER_WORDS:
        return NUMBER_WORDS[s]
    parts = s.split()
    if len(parts) == 2 and parts[0] in NUMBER_WORDS and parts[1] in NUMBER_WORDS:
        return NUMBER_WORDS[parts[0]] + NUMBER_WORDS[parts[1]]
    raise ValueError(f"Cannot parse number: {s}")


def _next_weekday(today: date, weekday: int) -> date:
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return today + timedelta(days=days_ahead)


def _last_weekday(today: date, weekday: int) -> date:
    days_behind = today.weekday() - weekday
    if days_behind <= 0:
        days_behind += 7
    return today - timedelta(days=days_behind)


def _add_months(d: date, n: int) -> date:
    month = d.month + n
    year = d.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    last_day = (
        (date(year, month % 12 + 1, 1) - timedelta(days=1)).day if month != 12 else 31
    )
    day = min(d.day, last_day)
    return d.replace(year=year, month=month, day=day)


def _normalize_month(s: str) -> str:
    """Remove trailing period from abbreviated month names."""
    return s.rstrip(".")


def _parse_month(s: str) -> int | None:
    key = _normalize_month(s.lower())
    return MONTHS.get(key)


def _ref_date(word: str, today: date) -> date:
    if word == "tomorrow":
        return today + timedelta(days=1)
    if word == "yesterday":
        return today - timedelta(days=1)
    return today


def _apply_delta(ref: date, n: int, unit: str, direction: str) -> date:
    sign = 1 if direction == "after" else -1
    if unit in ("day", "days"):
        return ref + timedelta(days=sign * n)
    if unit in ("week", "weeks"):
        return ref + timedelta(weeks=sign * n)
    if unit in ("month", "months"):
        return _add_months(ref, sign * n)
    if unit in ("year", "years"):
        return ref.replace(year=ref.year + sign * n)
    raise ValueError(f"Unknown unit: {unit}")


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)

    # "today"
    if s == "today":
        return today

    # "tomorrow"
    if s == "tomorrow":
        return today + timedelta(days=1)

    # "yesterday"
    if s == "yesterday":
        return today - timedelta(days=1)

    # "next <weekday>"
    m = re.fullmatch(r"next (\w+)", s)
    if m and m.group(1) in WEEKDAYS:
        return _next_weekday(today, WEEKDAYS[m.group(1)])

    # "last <weekday>"
    m = re.fullmatch(r"last (\w+)", s)
    if m and m.group(1) in WEEKDAYS:
        return _last_weekday(today, WEEKDAYS[m.group(1)])

    # "this <weekday>"
    m = re.fullmatch(r"this (\w+)", s)
    if m and m.group(1) in WEEKDAYS:
        return _next_weekday(today, WEEKDAYS[m.group(1)])

    # "in <n> days/weeks/months/years"
    m = re.fullmatch(r"in ([\w ]+?) (day|days|week|weeks|month|months|year|years)", s)
    if m:
        n = _parse_number(m.group(1))
        return _apply_delta(today, n, m.group(2), "after")

    # "<n> days/weeks/months/years ago"
    m = re.fullmatch(r"([\w ]+?) (day|days|week|weeks|month|months|year|years) ago", s)
    if m:
        n = _parse_number(m.group(1))
        return _apply_delta(today, n, m.group(2), "before")

    # "<n> days/weeks/months/years from now/today/tomorrow/yesterday"
    m = re.fullmatch(
        r"([\w ]+?) (day|days|week|weeks|month|months|year|years) from (now|today|tomorrow|yesterday)",
        s,
    )
    if m:
        n = _parse_number(m.group(1))
        ref = _ref_date(m.group(3), today)
        return _apply_delta(ref, n, m.group(2), "after")

    # "<n> days/weeks/months/years before now/today/tomorrow/yesterday"
    m = re.fullmatch(
        r"([\w ]+?) (day|days|week|weeks|month|months|year|years) before (now|today|tomorrow|yesterday)",
        s,
    )
    if m:
        n = _parse_number(m.group(1))
        ref = _ref_date(m.group(3), today)
        return _apply_delta(ref, n, m.group(2), "before")

    # "<n> days/weeks/months/years before/after <month> <day>, <year>"
    # supports "Dec. 1, 2025" and "December 1st, 2025"
    m = re.fullmatch(
        r"([\w ]+?) (day|days|week|weeks|month|months|year|years) (before|after) "
        r"(\w+\.?) (\d+)(?:st|nd|rd|th)?,? (\d{4})",
        s,
    )
    if m:
        month_val = _parse_month(m.group(4))
        if month_val is not None:
            n = _parse_number(m.group(1))
            ref = date(int(m.group(6)), month_val, int(m.group(5)))
            return _apply_delta(ref, n, m.group(2), m.group(3))

    # "<n> years and <m> months after/before <reference>"
    m = re.fullmatch(
        r"([\w ]+?) year(?:s)? and ([\w ]+?) month(?:s)? (after|before) (today|tomorrow|yesterday|now)",
        s,
    )
    if m:
        years = _parse_number(m.group(1))
        months = _parse_number(m.group(2))
        ref = _ref_date(m.group(4), today)
        total_months = years * 12 + months
        return _apply_delta(ref, total_months, "months", m.group(3))

    # exact date: "december 1st, 2025" or "dec. 1, 2025"
    m = re.fullmatch(r"(\w+\.?) (\d+)(?:st|nd|rd|th)?,? (\d{4})", s)
    if m:
        month_val = _parse_month(m.group(1))
        if month_val is not None:
            return date(int(m.group(3)), month_val, int(m.group(2)))

    # exact date: "2025-12-01" or "2025/12/01"
    m = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # exact date: "12/01/2025" or "12-01-2025"
    m = re.fullmatch(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", s)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))

    # "<n> days/weeks/months/years before/after <YYYY-MM-DD>"
    m = re.fullmatch(
        r"([\w ]+?) (day|days|week|weeks|month|months|year|years) (before|after) "
        r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})",
        s,
    )
    if m:
        n = _parse_number(m.group(1))
        ref = date(int(m.group(4)), int(m.group(5)), int(m.group(6)))
        return _apply_delta(ref, n, m.group(2), m.group(3))

    raise ValueError(f"Cannot parse date: {s!r}")
