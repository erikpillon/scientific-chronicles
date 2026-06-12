import os
import re


def parse_metadata_md(md_content):
    """Reuses the robust parsing logic to handle lists and protected keys."""
    metadata = {}
    current_key = None
    for line in md_content.split("\n"):
        if not line.strip():
            continue
        is_top_level = not line.startswith((" ", "\t"))
        if ":" in line and is_top_level:
            key, value = line.split(":", 1)
            key = key.strip()
            metadata[key] = value.strip().strip('"')
            current_key = key
        elif line.strip().startswith("-") and current_key:
            if not isinstance(metadata.get(current_key), list):
                metadata[current_key] = []
            item = line.strip()[1:].strip().strip('"')
            metadata[current_key].append(item)
    return metadata


def slugify(text):
    """Converts names and titles into URL-friendly filenames."""
    if not text:
        return ""
    # Lowercase, replace non-alphanumeric (except hyphens/dots in dates) with hyphens
    slug = re.sub(r"[^a-z0-9-]+", "-", str(text).lower())
    return slug.strip("-")


def rename_assets():
    folders = {"assets/scientists": "scientist", "assets/events": "event"}

    for folder, category in folders.items():
        if not os.path.exists(folder):
            continue

        for filename in os.listdir(folder):
            if filename.startswith("gemini-code") and filename.endswith(".md"):
                filepath = os.path.join(folder, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                parts = content.split("---")
                if len(parts) < 3:
                    continue

                metadata = parse_metadata_md(parts[1])

                if category == "scientist":
                    name = slugify(metadata.get("name", ""))
                    surname = slugify(metadata.get("surname", ""))
                    new_name = f"{name}-{surname}.md"
                else:  # event
                    date = metadata.get("date", "")
                    title = slugify(metadata.get("title", ""))
                    new_name = f"{date}-{title}.md"

                new_path = os.path.join(folder, new_name)
                if not os.path.exists(new_path):
                    os.rename(filepath, new_path)
                    print(f"Renamed: {filename} -> {new_name}")
                else:
                    print(f"Skipped: {new_name} already exists.")


if __name__ == "__main__":
    rename_assets()
