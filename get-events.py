import datetime
import argparse
import json
import os
import re


def parse_metadata_md(md_content):
    metadata = {}
    current_key = None
    # Parsing for YAML-like frontmatter with support for lists and nested-key protection
    for line in md_content.split("\n"):
        if not line.strip():
            continue

        # A key is considered top-level if the line does not start with whitespace
        is_top_level = not line.startswith((" ", "\t"))

        if ":" in line and is_top_level:
            key, value = line.split(":", 1)
            key = key.strip()
            metadata[key] = value.strip().strip('"')
            current_key = key
        elif line.strip().startswith("-") and current_key:
            # If we find a list item, ensure the current key holds a list
            if not isinstance(metadata.get(current_key), list):
                metadata[current_key] = []
            item = line.strip()[1:].strip().strip('"')
            metadata[current_key].append(item)
    return metadata


def main(start_date):
    target_month = start_date.month
    target_day = start_date.day
    scientists_dir = "assets/scientists"
    events_dir = "assets/events"

    if not os.path.exists(scientists_dir):
        print(f"Error: {scientists_dir} directory not found.")
        return

    print(
        f"Searching for scientific personalities and events on the week of {start_date.strftime('%B %d')}..."
    )
    found = False

    for file in os.listdir(scientists_dir):
        if file.endswith(".md"):
            with open(os.path.join(scientists_dir, file), "r", encoding="utf-8") as f:
                content = f.read()

            parts = content.split("---")
            if len(parts) < 3:
                continue

            metadata = parse_metadata_md(parts[1])
            name = f"{metadata.get('name', '')} {metadata.get('surname', '')}".strip()

            # Check both birth and death dates
            for key in ["birth_date", "death_date"]:
                date_val = metadata.get(key, "")
                if date_val and date_val != "unknown":
                    # Use regex to support negative years (BCE) which strptime doesn't handle
                    match = re.match(r"(-?\d+)-(\d{2})-(\d{2})", date_val)
                    if match:
                        _, month, day = map(int, match.groups())
                        if (
                            month == target_month
                            and day - target_day < 7
                            and day - target_day >= 0
                        ):
                            event_type = "Birth" if key == "birth_date" else "Death"
                            print(
                                f" - [{event_type}] {name} ({date_val}) - {metadata.get('headline', '')}"
                            )
                            found = True
    for file in os.listdir(events_dir):
        if file.endswith(".md"):
            with open(os.path.join(events_dir, file), "r", encoding="utf-8") as f:
                content = f.read()

            parts = content.split("---")
            if len(parts) < 3:
                continue

            metadata = parse_metadata_md(parts[1])
            date_val = metadata.get("date", "")
            if date_val and date_val != "unknown":
                match = re.match(r"(-?\d+)-(\d{2})-(\d{2})", date_val)
                if match:
                    _, month, day = map(int, match.groups())
                    if (
                        month == target_month
                        and day - target_day < 7
                        and day - target_day >= 0
                    ):
                        print(
                            f" - [Event] {metadata.get('title', '')} ({date_val}) - {metadata.get('headline', '')}"
                        )
                        found = True
    if not found:
        print("No events found for this day.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find scientist births and deaths for a specific date."
    )
    parser.add_argument(
        "start_date",
        help="Start date in YYYY-MM-DD format",
        type=lambda s: datetime.datetime.strptime(s, "%Y-%m-%d"),
    )
    args = parser.parse_args()
    main(args.start_date)
