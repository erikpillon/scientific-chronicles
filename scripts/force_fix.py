import os
import glob
import re

events_dir = "assets/other-events"
md_files_1 = glob.glob(os.path.join(events_dir, "0001*.md"))
md_files_2 = glob.glob(os.path.join(events_dir, "*-01-01*.md"))
md_files = list(set(md_files_1 + md_files_2))

for md_file in md_files:
    filename = os.path.basename(md_file)
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Determine what to do
    if filename.startswith("0001"):
        new_date = "0002" + filename[4:10]
    else:
        # Keep the existing year, just assume -01-01 is correct as we tried assessing it
        new_date = filename[:10]

    content = re.sub(r'^date:\s*.*$', f'date: {new_date}', content, flags=re.MULTILINE)
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    new_filename = new_date + filename[10:]
    new_filepath = os.path.join(events_dir, new_filename)
    
    if md_file != new_filepath:
        os.rename(md_file, new_filepath)
        print(f"Force renamed {filename} to {new_filename}")

print("Done with final pass.")
