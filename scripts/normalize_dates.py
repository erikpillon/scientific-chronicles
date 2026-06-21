#!/usr/bin/env python3
import json
import re
from pathlib import Path

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
}


def zero(num):
    return str(int(num)).zfill(2)


def parse_date(s):
    if not s or not isinstance(s, str):
        return None, "empty"
    orig = s.strip()
    s = orig
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s)
    s = s.strip()

    # ISO-ish:  YYYY-MM-DD or YYYY-M-D
    m = re.match(r"^(\d{1,4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        y, mo, d = m.groups()
        y = y.zfill(4)
        return f"{y}-{zero(mo)}-{zero(d)}", "iso"

    # Year-only like 1993
    m = re.match(r"^(\d{3,4})$", s)
    if m:
        y = m.group(1).zfill(4)
        return f"{y}-01-01", "year"

    # Patterns like '1900-02-18' (already ISO with 4-digit year and 2-digit month)
    m = re.match(r"^(\d{4})-(\d{2})$", s)
    if m:
        y, mo = m.groups()
        return f"{y}-{mo}-01", "year-month"

    # Month name day, year: 'January 03, 1888' or 'January 03 1888' or 'Jan 3 1888'
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{3,4})$", s)
    if m:
        mon, day, year = m.groups()
        mon_l = mon.lower()
        if mon_l[:3] in [k[:3] for k in MONTHS]:
            # allow short month names
            for k in MONTHS:
                if k.startswith(mon_l[:3]):
                    mo = MONTHS[k]
                    break
            return f"{year.zfill(4)}-{zero(mo)}-{zero(day)}", "mdy"

    # Day Month Year: '11 March 1702' or '11th March 1702'
    m = re.match(r"^(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+),?\s*(\d{3,4})$", s)
    if m:
        day, mon, year = m.groups()
        mon_l = mon.lower()
        for k in MONTHS:
            if k.startswith(mon_l[:3]):
                mo = MONTHS[k]
                break
        else:
            return None, "bad-month"
        return f"{year.zfill(4)}-{zero(mo)}-{zero(day)}", "dmy"

    # Month Day (no year) -> placeholder year 0001
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?$", s)
    if m:
        mon, day = m.groups()
        mon_l = mon.lower()
        for k in MONTHS:
            if k.startswith(mon_l[:3]):
                mo = MONTHS[k]
                break
        else:
            return None, "bad-month"
        return f"0001-{zero(mo)}-{zero(day)}", "md_no_year"

    # Day Month (no year) -> placeholder year 0001
    m = re.match(r"^(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)$", s)
    if m:
        day, mon = m.groups()
        mon_l = mon.lower()
        for k in MONTHS:
            if k.startswith(mon_l[:3]):
                mo = MONTHS[k]
                break
        else:
            return None, "bad-month"
        return f"0001-{zero(mo)}-{zero(day)}", "dm_no_year"

    # Numeric month/day with ordinal: 'March 4th' handled above; 'March 4th, 2007' handled above

    # Decades like '1960s-01-01' -> try to pick first 4 digits
    m = re.match(r"^(\d{4}).*", s)
    if m:
        y = m.group(1)
        # try to find month/day
        m2 = re.search(r"-(\d{1,2})-(\d{1,2})$", s)
        if m2:
            mo, d = m2.groups()
            return f"{y}-{zero(mo)}-{zero(d)}", "iso-extract"
        return f"{y.zfill(4)}-01-01", "year-extract"

    # centuries like '6th century AD' -> use midpoint year
    m = re.match(r"^(\d+)(?:th|st|nd|rd)?\s+century(?:\s+AD)?$", s, re.I)
    if m:
        cent = int(m.group(1))
        year = (cent - 1) * 100 + 50
        return f"{str(year).zfill(4)}-01-01", "century"

    # Around YYYY or 'Around 1469 AD'
    m = re.match(r"^(?:Around|around|c\.|circa)\s*(\d{3,4})", s)
    if m:
        y = m.group(1)
        return f"{y.zfill(4)}-01-01", "around"

    # BC or AD handling: extract year if AD, else fallback
    m = re.match(r"^(\d{1,4})\s*BC$", s, re.I)
    if m:
        return None, "bc"
    m = re.match(r"^(\d{1,4})\s*AD$", s, re.I)
    if m:
        y = m.group(1)
        return f"{y.zfill(4)}-01-01", "ad"

    # Special tokens
    if s.lower() in ("today", "unknown", "n/a"):
        return None, s.lower()

    return None, "unparsed"


def main():
    root = Path(__file__).resolve().parents[1]
    data_file = root / "extracted_historical_events.json"
    if not data_file.exists():
        print("extracted_historical_events.json not found at", data_file)
        return

    data = json.loads(data_file.read_text())
    changed = 0
    total = 0
    bc_warn = 0
    unparsed = 0

    for item in data:
        total += 1
        s = item.get("date")
        iso, reason = parse_date(s)
        if iso:
            if s != iso:
                item["date_original"] = s
                item["date"] = iso
                changed += 1
        else:
            # non-parseable -> store original and placeholder
            if s is not None:
                item["date_original"] = s
            item["date"] = "0001-01-01"
            unparsed += 1
            if reason == "bc":
                bc_warn += 1

    data_file.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    print(f"total={total} changed={changed} unparsed={unparsed} bc_warn={bc_warn}")


if __name__ == "__main__":
    main()
