from datetime import date, timedelta
import pytest
from study_planner import Subject, generate_schedule, summarize

START = date(2026, 11, 1)


def test_daily_hours_match():
    subs = [Subject("Math", START + timedelta(days=10), 3), Subject("Art", START + timedelta(days=5), 1)]
    rows = generate_schedule(subs, 4, start=START)
    per_day = {}
    for r in rows:
        per_day[r["date"]] = per_day.get(r["date"], 0) + r["hours"]
    assert all(h == 4 for h in per_day.values())


def test_harder_subject_gets_more_time():
    d = START + timedelta(days=7)
    rows = generate_schedule([Subject("Hard", d, 3), Subject("Easy", d, 1)], 4, start=START)
    t = summarize(rows)
    assert t["Hard"] > t["Easy"]


def test_no_study_after_exam():
    exam = START + timedelta(days=2)
    rows = generate_schedule([Subject("A", exam, 2), Subject("B", START + timedelta(days=6), 2)], 3, start=START)
    assert all(r["date"] <= exam for r in rows if r["subject"] == "A")


def test_past_exam_rejected():
    with pytest.raises(ValueError):
        generate_schedule([Subject("A", START - timedelta(days=1), 2)], 3, start=START)


def test_bad_hours_rejected():
    with pytest.raises(ValueError):
        generate_schedule([Subject("A", START + timedelta(days=1), 2)], 0, start=START)
