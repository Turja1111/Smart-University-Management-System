"""
Helpers for class routine JSON (theory + lab) and API `by_day` views.
"""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

# PDF: theory 1hr 20min, lab 3hr
THEORY_BLOCK_MINUTES = 80
LAB_BLOCK_MINUTES = 180

DAY_ABBR_TO_WEEKDAY = {
    'MON': 'Monday',
    'TUE': 'Tuesday',
    'WED': 'Wednesday',
    'THU': 'Thursday',
    'FRI': 'Friday',
    'SAT': 'Saturday',
    'SUN': 'Sunday',
}

_WEEKDAY_ORDER = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6,
}

_TIME_RE = re.compile(r'^\s*(\d{1,2}):(\d{2})\s*([AP]M)\s*$', re.I)


def normalize_weekday_token(day: str | None) -> str | None:
    if not day:
        return None
    d = str(day).strip().upper()
    if d in DAY_ABBR_TO_WEEKDAY:
        return DAY_ABBR_TO_WEEKDAY[d]
    if d in _WEEKDAY_ORDER:
        return d
    return day.strip()


def parse_time_minutes(t: str | None) -> int | None:
    """Minutes since midnight for sorting; None if unparsable."""
    if not t:
        return None
    m = _TIME_RE.match(t.strip())
    if not m:
        return None
    hh = int(m.group(1))
    mm = int(m.group(2))
    ap = m.group(3).upper()
    if ap == 'PM' and hh != 12:
        hh += 12
    if ap == 'AM' and hh == 12:
        hh = 0
    return hh * 60 + mm


def add_minutes_to_clock(time_str: str, minutes: int) -> str:
    m = _TIME_RE.match((time_str or '').strip())
    if not m:
        return time_str
    hh = int(m.group(1))
    mm = int(m.group(2))
    ap = m.group(3).upper()
    if ap == 'PM' and hh != 12:
        hh += 12
    if ap == 'AM' and hh == 12:
        hh = 0
    base = datetime(2000, 1, 1, hh, mm)
    out = base + timedelta(minutes=minutes)
    return out.strftime('%I:%M %p').lstrip('0').replace(' 0', ' ')


def section_to_slots(section: dict[str, Any]) -> list[dict[str, Any]]:
    """Build normalized slot list from a `sections` item in routine_extracted.json."""
    slots: list[dict[str, Any]] = []
    theory = section.get('theory') or {}
    for mtg in theory.get('meetings') or []:
        day_raw = (mtg.get('day') or '').strip()
        wd = normalize_weekday_token(day_raw)
        if not wd:
            continue
        start = (mtg.get('time') or '').strip()
        room = (mtg.get('room') or '').strip()
        slots.append({
            'weekday': wd,
            'start_time': start,
            'end_time': add_minutes_to_clock(start, THEORY_BLOCK_MINUTES),
            'room': room or '—',
            'kind': 'theory',
        })

    lab = section.get('lab')
    if lab and lab.get('day'):
        wd = normalize_weekday_token(str(lab['day']).strip())
        start = (lab.get('time') or '').strip()
        if wd and start:
            room = (lab.get('room') or '').strip()
            slots.append({
                'weekday': wd,
                'start_time': start,
                'end_time': add_minutes_to_clock(start, LAB_BLOCK_MINUTES),
                'room': room or '—',
                'kind': 'lab',
            })

    return slots


def schedule_slots_from_course(schedule: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Slots list from Course.schedule (new format)."""
    if not schedule:
        return []
    slots = schedule.get('slots')
    if isinstance(slots, list) and slots:
        return slots
    return legacy_schedule_to_slots(schedule)


def legacy_schedule_to_slots(schedule: dict[str, Any]) -> list[dict[str, Any]]:
    """Best-effort conversion from older {"days": [...], "time": "...", "room": "..."}."""
    days = schedule.get('days') or []
    time = schedule.get('time')
    room = schedule.get('room') or '—'
    if not days or not time:
        return []
    out = []
    for d in days:
        wd = normalize_weekday_token(str(d))
        if not wd:
            wd = str(d)
        out.append({
            'weekday': wd,
            'start_time': time,
            'end_time': time,
            'room': str(room),
            'kind': 'class',
        })
    return out


def build_by_day_for_enrollments(
    enrollments: list,
) -> dict[str, list[dict[str, Any]]]:
    """
    enrollments: queryset or list of Enrollment with .course loaded.
    Returns { \"Monday\": [...], ... } with merged / sorted entries.
    """
    bucket: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for e in enrollments:
        course = e.course
        slots = schedule_slots_from_course(course.schedule)
        for slot in slots:
            wd = slot.get('weekday')
            if not wd:
                continue
            bucket[wd].append({
                'course_code': course.code,
                'course_name': course.name,
                'start_time': slot.get('start_time') or '—',
                'end_time': slot.get('end_time') or '—',
                'room': slot.get('room') or '—',
                'kind': slot.get('kind', 'class'),
            })

    for wd in bucket:
        bucket[wd].sort(key=lambda row: (parse_time_minutes(row['start_time']) or 0, row['course_code']))

    return dict(bucket)


def department_code_from_course_code(course_code: str) -> str:
    """e.g. CSE101 -> CSE, CSEA250 -> CSEA."""
    m = re.match(r'^([A-Z]+)', (course_code or '').strip().upper())
    return m.group(1) if m else 'GEN'


def iter_conflict_intervals(course_code: str, schedule: dict[str, Any] | None) -> list[tuple[str, int, int, str]]:
    """
    Yield (weekday, start_min, end_min, course_code) for overlap detection.
    """
    if not schedule:
        return []
    slots = schedule.get('slots')
    out: list[tuple[str, int, int, str]] = []
    if isinstance(slots, list) and slots:
        for slot in slots:
            wd = slot.get('weekday')
            if not wd:
                continue
            sm = parse_time_minutes(slot.get('start_time'))
            em = parse_time_minutes(slot.get('end_time'))
            if sm is None:
                continue
            if em is None or em <= sm:
                em = sm + 60
            out.append((wd, sm, em, course_code))
        return out

    # Legacy single block
    leg = legacy_schedule_to_slots(schedule)
    for slot in leg:
        wd = slot.get('weekday')
        sm = parse_time_minutes(slot.get('start_time'))
        em = parse_time_minutes(slot.get('end_time'))
        if not wd or sm is None:
            continue
        if em is None or em <= sm:
            em = sm + 60
        out.append((wd, sm, em, course_code))
    return out


def intervals_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """[start, end) style overlap."""
    sa, ea = a
    sb, eb = b
    return not (ea <= sb or eb <= sa)


def department_display_name(code: str) -> str:
    known = {
        'CSE': 'Computer Science and Engineering',
        'EEE': 'Electrical and Electronic Engineering',
        'MAT': 'Mathematics',
        'PHY': 'Physics',
        'CHE': 'Chemistry',
        'ENG': 'English',
        'ECO': 'Economics',
        'STA': 'Statistics',
    }
    if code in known:
        return known[code]
    return f'{code} Department'
