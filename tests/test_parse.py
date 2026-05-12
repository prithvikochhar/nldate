from datetime import date
from nldate import parse


TODAY = date(2025, 3, 15)  # Saturday


def test_today():
    assert parse("today", today=TODAY) == date(2025, 3, 15)


def test_tomorrow():
    assert parse("tomorrow", today=TODAY) == date(2025, 3, 16)


def test_yesterday():
    assert parse("yesterday", today=TODAY) == date(2025, 3, 14)


def test_next_tuesday():
    assert parse("next tuesday", today=TODAY) == date(2025, 3, 18)


def test_last_monday():
    assert parse("last monday", today=TODAY) == date(2025, 3, 10)


def test_in_3_days():
    assert parse("in 3 days", today=TODAY) == date(2025, 3, 18)


def test_in_two_weeks():
    assert parse("in two weeks", today=TODAY) == date(2025, 3, 29)


def test_5_days_ago():
    assert parse("5 days ago", today=TODAY) == date(2025, 3, 10)


def test_3_days_from_now():
    assert parse("3 days from now", today=TODAY) == date(2025, 3, 18)


def test_5_days_before_exact_date():
    assert parse("5 days before december 1st, 2025", today=TODAY) == date(2025, 11, 26)


def test_exact_date_with_ordinal():
    assert parse("december 1st, 2025", today=TODAY) == date(2025, 12, 1)


def test_exact_date_iso():
    assert parse("2025-12-01", today=TODAY) == date(2025, 12, 1)


def test_in_2_months():
    assert parse("in 2 months", today=TODAY) == date(2025, 5, 15)


def test_1_year_after_tomorrow():
    assert parse("1 year and 2 months after yesterday", today=TODAY) == date(2026, 5, 14)


def test_default_today():
    result = parse("today")
    assert result == date.today()
