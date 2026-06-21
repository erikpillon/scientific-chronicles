import os
import json
import time
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from google import genai
from google.genai import types


# 1. Define the desired output structure using Pydantic
class HistoricalEvent(BaseModel):
    date: str
    event_title: str
    description: str


class DayEventsList(BaseModel):
    events: list[HistoricalEvent]


def fetch_page_text(url: str) -> str:
    """Fetches the webpage content and extracts readable text to minimize token usage."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        # Clean up the HTML to only pass meaningful content to Gemini
        soup = BeautifulSoup(response.text, "html.parser")

        # Strip away scripts, styles, navbars, and footers if possible.
        # Difford's guide articles usually sit inside main or specific article blocks,
        # but extracting body text generally works safely.
        for element in soup(["script", "style", "nav", "footer"]):
            element.decompose()

        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def extract_events_with_gemini(
    page_text: str, date_str: str, client: genai.Client
) -> list:
    """Uses Gemini API to parse raw text and return a structured list of events."""
    if not page_text:
        return []

    prompt = f"""
    Analyze the following web page text from Difford's Guide 'On This Day' for {date_str}.
    Extract all historical events, birthdays, or milestones mentioned that happened on this day.
    
    CRITICAL INSTRUCTIONS:
    - Focus strictly on the historical event itself (e.g., 'In 1961, Lady Diana Spencer was born...').
    - Do NOT include information about the cocktail/drink paired with the event.
    - Exclude the drink recipes or bartending facts completely.
    
    Text to process:
    {page_text}
    """

    try:
        # Utilizing gemini-2.5-flash as it is exceptionally fast and accurate for data extraction
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DayEventsList,
                temperature=0.1,  # Low temperature for precise facts extraction
            ),
        )

        # The response text is guaranteed to parse into our Pydantic schema structure
        data = json.loads(response.text)
        return data.get("events", [])

    except Exception as e:
        print(f"Error calling Gemini API for {date_str}: {e}")
        return []


def create_dates_list(start_date: str, end_date: str) -> list:
    """Creates a list of date dictionaries for the specified range."""
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=1)

    dates_list = []
    while start <= end:
        dates_list.append(
            {"month": start.strftime("%B").lower(), "day": start.strftime("%d")}
        )
        start += delta

    return dates_list


def main():
    # Initialize the Gemini Client. It automatically picks up GEMINI_API_KEY from your local environment.
    if not os.environ.get("GEMINI_API_KEY"):
        print("Error: GEMINI_API_KEY environment variable is not set.")
        return

    client = genai.Client()

    # Example target list: you can build this list programmatically for multiple days/months
    target_dates = create_dates_list("2023-01-01", "2023-12-31")  # Full year of 2023

    print(f"Total dates to process: {len(target_dates)}")

    all_extracted_events = []
    output_filename = "extracted_historical_events.json"

    for date_info in target_dates:
        month = date_info["month"]
        day = date_info["day"]
        date_str = f"{month} {day}"

        url = f"https://www.diffordsguide.com/on-this-day/{month}/{day}"
        print(f"Processing: {url}...")

        # 1. Scrape webpage text
        page_text = fetch_page_text(url)

        # 2. Extract with Gemini
        day_events = extract_events_with_gemini(page_text, date_str, client)
        print(f"-> Successfully extracted {len(day_events)} events for {date_str}.")

        all_extracted_events.extend(day_events)

        # Polite throttling between network and API requests
        time.sleep(2)

    # 3. Save the results to an external local file
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(all_extracted_events, f, indent=4, ensure_ascii=False)

    print(f"\nParsing complete! All events successfully saved to '{output_filename}'.")


if __name__ == "__main__":
    main()
