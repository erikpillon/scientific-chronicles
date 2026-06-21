import os
import glob
import json
import re
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

events_dir = "assets/other-events"
md_files_1 = glob.glob(os.path.join(events_dir, "0001*.md"))
md_files_2 = glob.glob(os.path.join(events_dir, "*-01-01*.md"))
md_files = list(set(md_files_1 + md_files_2))

events_to_fix = []

for md_file in md_files:
    filename = os.path.basename(md_file)
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    title_match = re.search(r'title:\s*"([^"]+)"', content)
    if not title_match:
        title_match = re.search(r'title:\s*(.+)', content)
        if not title_match:
            continue
    
    title = title_match.group(1).strip('"\'')
    events_to_fix.append({
        "filename": filename,
        "filepath": md_file,
        "title": title,
        "content_preview": content[:150]
    })

print(f"Found {len(events_to_fix)} files to process.")
if not events_to_fix: exit(0)

chunk_size = 5
all_dates = {}

for i in range(0, len(events_to_fix), chunk_size):
    chunk = events_to_fix[i:i+chunk_size]
    print(f"Processing chunk {i//chunk_size + 1} / {(len(events_to_fix)+chunk_size-1)//chunk_size}")
    
    events_list = []
    for ev in chunk:
        events_list.append(f"Filename: {ev['filename']}\nTitle: {ev['title']}\n")
    
    prompt = f"""
    Determine the ACTUAL EXACT DATE (YYYY-MM-DD) for each event. Do not use '-01-01' unless the exact month and day are genuinely unknown.
    RULES:
    1. RECURRING annual events/holidays use year '0002' (e.g. '0002-12-25').
    2. Historical single events use the actual historical year and date (e.g. '1997-12-18').
    3. Return a JSON array of objects. Each object must have "filename" (exact match) and "date" (YYYY-MM-DD).
    
    Events:
    {"".join(events_list)}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        data = json.loads(response.text)
        for item in data:
            if "filename" in item and "date" in item:
                all_dates[item["filename"]] = item["date"]
    except Exception as e:
        print(f"Error querying Gemini: {e}")

# Apply changes
for ev in events_to_fix:
    filename = ev["filename"]
    filepath = ev["filepath"]
    if filename not in all_dates:
        print(f"Missing from response: {filename}")
        continue
        
    new_date = all_dates[filename]
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', new_date):
        print(f"Invalid date format for {filename}: {new_date}")
        continue
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    content = re.sub(r'^date:\s*.*$', f'date: {new_date}', content, flags=re.MULTILINE)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    new_filename = new_date + filename[10:]
    new_filepath = os.path.join(events_dir, new_filename)
    
    if filepath != new_filepath:
        os.rename(filepath, new_filepath)
        print(f"Renamed {filename} to {new_filename}")

print("Finished updating event dates.")
