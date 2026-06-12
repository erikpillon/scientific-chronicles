import os
import re
import shutil


def parse_metadata_md(md_content):
    metadata = {}
    current_key = None
    for line in md_content.split("\n"):
        if not line.strip():
            continue
        is_top_level = not line.startswith((" ", "\t"))
        if ":" in line and is_top_level:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip('"')
            current_key = key.strip()
        elif line.strip().startswith("-") and current_key:
            if not isinstance(metadata.get(current_key), list):
                metadata[current_key] = []
            metadata[current_key].append(line.strip()[1:].strip().strip('"'))
    return metadata


def slugify(text):
    return re.sub(r"[^a-z0-9-]+", "-", str(text).lower()).strip("-")


def update_md_image(filepath, new_image_name):
    """Updates the image field in the frontmatter while preserving the rest of the file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---")
    if len(parts) < 3:
        return

    lines = parts[1].split("\n")
    updated_lines = []
    found = False
    for line in lines:
        if line.strip().startswith("image:"):
            updated_lines.append(f'image: "{new_image_name}"')
            found = True
        else:
            updated_lines.append(line)

    if not found:
        updated_lines.append(f'image: "{new_image_name}"')

    parts[1] = "\n".join(updated_lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("---".join(parts))


def get_all_subjects(base_dir):
    """Returns a list of dicts containing metadata and file paths for all entries."""
    subjects = []
    folders = {"assets/scientists": "scientist", "assets/events": "event"}
    for folder, cat in folders.items():
        full_folder = os.path.join(base_dir, folder)
        if not os.path.exists(full_folder):
            continue
        for file in os.listdir(full_folder):
            if file.endswith(".md"):
                path = os.path.join(full_folder, file)
                with open(path, "r", encoding="utf-8") as f:
                    parts = f.read().split("---")
                    if len(parts) < 3:
                        continue
                    meta = parse_metadata_md(parts[1])
                    # Create a searchable string based on name/title
                    search_text = f"{meta.get('name', '')} {meta.get('surname', '')} {meta.get('title', '')}".lower()
                    subjects.append({
                        "path": path,
                        "category": cat,
                        "search_text": search_text,
                        "meta": meta,
                    })
    return subjects


def organize_images():
    base_dir = os.getcwd()
    assets_dir = os.path.join(base_dir, "assets")
    subjects = get_all_subjects(base_dir)

    image_files = [
        f
        for f in os.listdir(assets_dir)
        if f.startswith("ChatGPT Image")
        and f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    for img_name in image_files:
        img_path = os.path.join(assets_dir, img_name)
        # Clean up the image name to find keywords
        clean_img_name = img_name.replace("ChatGPT Image", "").replace("-", " ").lower()

        best_match = None
        max_overlap = 0

        for sub in subjects:
            # Count how many words from the subject's name/title are in the image filename
            keywords = [w for w in sub["search_text"].split() if len(w) > 2]
            overlap = sum(1 for kw in keywords if kw in clean_img_name)

            if overlap > max_overlap:
                max_overlap = overlap
                best_match = sub

        if best_match and max_overlap > 0:
            ext = os.path.splitext(img_name)[1]
            if best_match["category"] == "scientist":
                new_img_name = f"{slugify(best_match['meta'].get('name'))}-{slugify(best_match['meta'].get('surname'))}{ext}"
            else:
                new_img_name = f"{best_match['meta'].get('date')}-{slugify(best_match['meta'].get('title'))}{ext}"

            new_img_path = os.path.join(assets_dir, new_img_name)

            # Perform the rename and update metadata
            os.rename(img_path, new_img_path)
            update_md_image(best_match["path"], new_img_name)
            print(
                f"Matched & Processed: '{img_name}' -> '{new_img_name}' for {best_match['path']}"
            )
        else:
            print(f"Could not confidently guess subject for: {img_name}")


if __name__ == "__main__":
    organize_images()
