#!/usr/bin/env python3
import json
import re
from pathlib import Path


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    s = s.strip("-")
    return s or "untitled"


def safe_write(path: Path, content: str):
    if path.exists():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def make_frontmatter(item):
    title = item.get("event_title") or item.get("title") or "Untitled"
    date = item.get("date") or "0001-01-01"
    date_original = item.get("date_original")
    headline = title
    fm = []
    fm.append("---")
    fm.append(f'title: "{title.replace('"', '\\"')}"')
    fm.append(f"date: {date}")
    if date_original:
        fm.append(f'date_original: "{date_original.replace('"', '\\"')}"')
    fm.append('event_type: "Other"')
    fm.append("disciplines: []")
    fm.append("associated_people: []")
    fm.append(f'headline: "{headline.replace('"', '\\"')}"')
    fm.append('image: ""')
    fm.append("---")
    fm.append("")
    return "\n".join(fm)


def main():
    root = Path(__file__).resolve().parents[1]
    data_file = root / "extracted_historical_events.json"
    out_dir = root / "assets" / "other-events"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(data_file.read_text())
    used = {}
    created = 0
    for item in data:
        date = item.get("date") or "0001-01-01"
        title = item.get("event_title") or "Untitled"
        slug = slugify(title)
        base = f"{date}-{slug}.md"
        path = out_dir / base
        # ensure unique
        i = 1
        while path.exists():
            path = out_dir / f"{date}-{slug}-{i}.md"
            i += 1

        fm = make_frontmatter(item)
        body = item.get("description", "").strip() + "\n"
        content = fm + "\n" + body
        path.write_text(content, encoding="utf-8")
        created += 1

    print(f"created {created} files in {out_dir}")


if __name__ == "__main__":
    main()
