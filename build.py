"""Build every calendar in calendars.toml from its CSV into an .ics file.

Standard library only, so the GitHub Action needs no installs. Run locally
with `python3 build.py`. Any bad row stops the build, so a broken CSV never
replaces a working feed.
"""

import csv
import hashlib
import os
import sys
import tomllib
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))


def escape(text):
    return (text.replace("\\", "\\\\").replace(";", "\\;")
                .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    """Split a content line into 75-octet chunks, as RFC 5545 requires."""
    raw = line.encode("utf-8")
    parts, limit = [], 75
    while len(raw) > limit:
        cut = limit
        while raw[cut] & 0xC0 == 0x80:  # don't split a multi-byte character
            cut -= 1
        parts.append(raw[:cut].decode("utf-8"))
        raw, limit = raw[cut:], 74  # continuation lines start with a space
    parts.append(raw.decode("utf-8"))
    return "\r\n ".join(parts)


def fill(template, row, where):
    try:
        return template.format_map(row).strip()
    except KeyError as e:
        sys.exit(f"{where}: no column {e} in the CSV")


def build(cal, stamp):
    path = os.path.join(ROOT, cal["csv"])
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//caydenwe//calendars//EN",
        "CALSCALE:GREGORIAN",
        f"X-WR-CALNAME:{escape(cal['name'])}",
        "X-PUBLISHED-TTL:PT6H",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H",
    ]
    seen = set()
    for n, row in enumerate(rows, start=2):  # line 1 is the header
        where = f"{cal['csv']} line {n}"
        if not any((v or "").strip() for v in row.values()):
            continue  # blank row
        try:
            start = datetime.strptime(row[cal["start"]].strip(), cal["date_format"]).date()
            end_col = (row.get(cal.get("end", "")) or "").strip()
            end = datetime.strptime(end_col, cal["date_format"]).date() if end_col else start
        except (KeyError, ValueError) as e:
            sys.exit(f"{where}: bad date ({e})")
        if end < start:
            sys.exit(f"{where}: ends before it starts")

        title = fill(cal["title"], row, where)
        # Stable ID: same title on the same day is the same event across builds,
        # so subscribers' apps update it in place instead of re-creating it.
        key = f"{cal['output']}|{title}|{start.isoformat()}"
        if key in seen:
            sys.exit(f"{where}: duplicate of an earlier row ({title}, {start})")
        seen.add(key)
        uid = hashlib.sha1(key.encode()).hexdigest()[:20] + "@caydenwe.calendars"

        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{stamp}",
            f"SUMMARY:{escape(title)}",
            f"DTSTART;VALUE=DATE:{start:%Y%m%d}",
            f"DTEND;VALUE=DATE:{end + timedelta(days=1):%Y%m%d}",  # exclusive
        ]
        if cal.get("location"):
            location = fill(cal["location"], row, where)
            if location:
                lines.append(f"LOCATION:{escape(location)}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")

    with open(os.path.join(ROOT, cal["output"]), "w", encoding="utf-8", newline="") as fh:
        fh.write("".join(fold(l) + "\r\n" for l in lines))
    print(f"{cal['output']}: {len(seen)} events")


def main():
    with open(os.path.join(ROOT, "calendars.toml"), "rb") as fh:
        calendars = tomllib.load(fh)["calendar"]
    # A fixed DTSTAMP keeps the output identical when the CSV hasn't changed.
    epoch = int(os.environ.get("SOURCE_DATE_EPOCH", "0"))
    stamp = datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for cal in calendars:
        build(cal, stamp)


if __name__ == "__main__":
    main()
