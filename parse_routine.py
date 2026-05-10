import argparse
import json
import re
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent
DEFAULT_PDF = ROOT / "Routine.pdf"
OUTPUT_JSON = ROOT / "routine_extracted.json"

# e.g. CSE101-01, CSE250-12A, CSE490D-01, CSE799A-01, EEE362-01
COURSE_FULL_RE = re.compile(r"^([A-Z]{2,4}\d{2,3}[A-Z]?)-(.+)$")


def _split_plus(v: str) -> list[str]:
    return [p.strip() for p in v.split("+") if p.strip()]


def _parse_course(course: str) -> dict:
    """
    Examples:
      - CSE101-01   -> code=CSE101, section=01
      - CSE250-12A  -> code=CSE250, section=12A
      - CSE490D-01  -> code=CSE490D, section=01
      - CSE799A-01  -> code=CSE799A, section=01
    """
    course = (course or "").strip()
    m = COURSE_FULL_RE.match(course)
    if not m:
        return {"full": course, "code": course or None, "section": None}
    return {"full": course, "code": m.group(1), "section": m.group(2)}


def _parse_people_csv(v: str) -> list[str]:
    v = (v or "").strip()
    if not v:
        return []
    return [p.strip() for p in v.split(",") if p.strip()]


def _norm_empty(v: str | None) -> str | None:
    if v is None:
        return None
    v = str(v).strip()
    return v if v else None


def _build_theory_meetings(theory_day: str | None, theory_time: str | None, theory_room: str | None):
    """
    Supports cases like:
      theory_day  = "MON+WED"
      theory_time = "2:00 PM"

    And special cases like:
      theory_day  = "SUN+SUN"
      theory_time = "11:00 AM+12:30 PM"
    """
    if not theory_day or not theory_time:
        return []

    days = _split_plus(theory_day) if "+" in theory_day else [theory_day.strip()]
    times = _split_plus(theory_time) if "+" in theory_time else [theory_time.strip()]

    # Common case: two days share one time (e.g. "MON+WED" + "2:00 PM")
    if len(times) == 1 and len(days) > 1:
        return [{"day": d, "time": times[0], "room": theory_room} for d in days]

    # Less common: one day with multiple times (e.g. "SUN" + "11:00 AM+12:30 PM")
    if len(days) == 1 and len(times) > 1:
        return [{"day": days[0], "time": t, "room": theory_room} for t in times]

    # If the PDF encodes multiple slots, they should align 1:1 (best effort).
    if len(days) == len(times):
        return [{"day": d, "time": t, "room": theory_room} for d, t in zip(days, times)]

    # Otherwise store a single "raw" meeting
    return [{"day": theory_day, "time": theory_time, "room": theory_room}]


def _normalize_table_row(row: list) -> list[str]:
    out: list[str] = []
    for c in row:
        if c is None:
            out.append("")
        else:
            out.append(str(c).strip())
    return out


def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    """Read Routine.pdf with pdfplumber: text + first table per page."""
    pages_out: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            raw = page.extract_table()
            tables: list[list[list[str]]] = []
            if raw:
                tables.append([_normalize_table_row(r) for r in raw])
            pages_out.append({"page": i, "text": text, "tables": tables})
    return pages_out


def parse_pages_to_sections(pages: list[dict]) -> list[dict]:
    sections: list[dict] = []

    for page in pages:
        for table in page.get("tables", []) or []:
            if not table or len(table) < 2:
                continue

            header = table[0]
            # Expect the canonical header shape for these routines.
            if not header or (header[0] or "").strip().lower() != "course":
                continue

            for row in table[1:]:
                if not row or len(row) < 5:
                    continue

                # Pad to 9 cells to avoid index errors.
                row = list(row) + [""] * (9 - len(row))
                course, theory_initial, theory_day, theory_time, theory_room, lab_faculty, lab_day, lab_time, lab_room = row[:9]

                course = (course or "").strip()
                if not course:
                    continue

                course_info = _parse_course(course)

                theory_day = _norm_empty(theory_day)
                theory_time = _norm_empty(theory_time)
                theory_room = _norm_empty(theory_room)

                # Some rows have placeholders like XXX.
                if theory_day == "XXX":
                    theory_day = None
                if theory_room == "XXX":
                    theory_room = None

                lab_faculty = _norm_empty(lab_faculty)
                lab_day = _norm_empty(lab_day)
                lab_time = _norm_empty(lab_time)
                lab_room = _norm_empty(lab_room)

                lab = None
                if any([lab_faculty, lab_day, lab_time, lab_room]):
                    lab = {
                        "faculty": _parse_people_csv(lab_faculty),
                        "day": lab_day,
                        "time": lab_time,
                        "room": lab_room,
                    }

                section = {
                    "page": page.get("page"),
                    "course_full": course_info["full"],
                    "course_code": course_info["code"],
                    "section": course_info["section"],
                    "theory": {
                        "initial": _norm_empty(theory_initial),
                        "meetings": _build_theory_meetings(theory_day, theory_time, theory_room),
                    },
                    "lab": lab,
                }
                sections.append(section)

    # De-duplicate (course_full is unique in this routine; keep first occurrence)
    seen: set[str] = set()
    deduped: list[dict] = []
    for s in sections:
        key = s["course_full"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(s)
    return deduped


def main():
    parser = argparse.ArgumentParser(description="Extract class routine tables from Routine.pdf to JSON.")
    parser.add_argument(
        "--pdf",
        type=Path,
        default=DEFAULT_PDF,
        help=f"Path to PDF (default: {DEFAULT_PDF})",
    )
    parser.add_argument(
        "--from-json",
        type=Path,
        default=None,
        help="Re-parse existing routine_extracted.json (use its 'pages' only; no PDF read).",
    )
    args = parser.parse_args()

    if args.from_json:
        raw = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        pages = raw["pages"] if isinstance(raw, dict) and "pages" in raw else raw
        source_name = str(args.from_json)
    else:
        pdf_path = Path(args.pdf)
        if not pdf_path.is_file():
            raise SystemExit(f"PDF not found: {pdf_path}")
        pages = extract_pdf_pages(pdf_path)
        source_name = pdf_path.name

    sections = parse_pages_to_sections(pages)

    wrapped = {
        "source_pdf": source_name,
        "pages": pages,
        "sections": sections,
        "stats": {
            "pages": len(pages),
            "sections": len(sections),
        },
    }

    OUTPUT_JSON.write_text(json.dumps(wrapped, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUTPUT_JSON} — {len(pages)} pages, {len(sections)} sections.")


if __name__ == "__main__":
    main()
