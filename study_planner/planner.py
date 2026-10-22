"""Core scheduling logic. Pure Python: no API, no cost."""
import csv
from dataclasses import dataclass
from datetime import date, timedelta

DIFFICULTY = {"easy": 1, "medium": 2, "hard": 3}


@dataclass
class Subject:
    name: str
    exam_date: date
    difficulty: int = 2  # 1 = easy, 2 = medium, 3 = hard


def _split_hours(total, weights, step=0.5):
    """Split `total` hours by weight in `step` blocks (largest remainder)."""
    units = int(round(total / step))
    wsum = sum(weights.values())
    if units == 0 or wsum == 0:
        return {}
    raw = {k: units * w / wsum for k, w in weights.items()}
    base = {k: int(v) for k, v in raw.items()}
    left = units - sum(base.values())
    for k in sorted(raw, key=lambda k: raw[k] - base[k], reverse=True)[:left]:
        base[k] += 1
    return {k: v * step for k, v in base.items() if v > 0}


def generate_schedule(subjects, hours_per_day, start=None):
    """Return a list of {date, subject, hours} rows.

    Weight for each subject on each day = difficulty / (days_left + 1),
    so harder subjects and closer exams get more time.
    """
    start = start or date.today()
    if not subjects:
        raise ValueError("Add at least one subject.")
    if hours_per_day <= 0:
        raise ValueError("Hours per day must be greater than 0.")
    for s in subjects:
        if s.difficulty not in (1, 2, 3):
            raise ValueError(f"{s.name}: difficulty must be 1, 2 or 3.")
        if s.exam_date < start:
            raise ValueError(f"{s.name}: exam date is in the past.")

    rows, day = [], start
    last = max(s.exam_date for s in subjects)
    while day <= last:
        active = [s for s in subjects if s.exam_date >= day]
        weights = {s.name: s.difficulty / ((s.exam_date - day).days + 1) for s in active}
        for name, hrs in _split_hours(hours_per_day, weights).items():
            rows.append({"date": day, "subject": name, "hours": hrs})
        day += timedelta(days=1)
    return rows


def summarize(rows):
    """Total hours per subject."""
    out = {}
    for r in rows:
        out[r["subject"]] = out.get(r["subject"], 0) + r["hours"]
    return out


def export_csv(rows, path="study_plan.csv"):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["date", "subject", "hours"])
        w.writeheader()
        w.writerows(rows)
    return path


def export_ics(rows, path="study_plan.ics"):
    """All-day calendar events you can import into Google Calendar."""
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//ai-study-planner//EN"]
    for i, r in enumerate(rows):
        d = r["date"]
        nxt = d + timedelta(days=1)
        lines += [
            "BEGIN:VEVENT",
            f"UID:study-{i}-{d:%Y%m%d}@ai-study-planner",
            f"DTSTAMP:{d:%Y%m%d}T000000Z",
            f"DTSTART;VALUE=DATE:{d:%Y%m%d}",
            f"DTEND;VALUE=DATE:{nxt:%Y%m%d}",
            f"SUMMARY:Study {r['subject']} ({r['hours']}h)",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines))
    return path
