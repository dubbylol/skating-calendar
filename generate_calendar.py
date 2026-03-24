import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re

URL = "https://www.ashlandskateland.com/calendar.html"

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

def parse_time_range(text):
    match = re.search(r'(\d{1,2}(:\d{2})?)(am|pm)-(\d{1,2}(:\d{2})?)(am|pm)', text, re.I)
    if not match:
        return None

    def to_24(t, ampm):
        h, m = (t.split(":") + ["00"])[:2]
        h = int(h)
        m = int(m)
        if ampm.lower() == "pm" and h != 12:
            h += 12
        if ampm.lower() == "am" and h == 12:
            h = 0
        return h, m

    sh, sm = to_24(match.group(1), match.group(3))
    eh, em = to_24(match.group(4), match.group(6))

    return sh, sm, eh, em

def fetch_events():
    html = requests.get(URL).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")

    lines = [clean(l) for l in text.split("\n") if l.strip()]

    events = []
    current_day = None

    for line in lines:
        if line.isdigit():
            current_day = int(line)
            continue

        if current_day:
            time = parse_time_range(line)
            if time:
                title = re.sub(r'\d.*', '', line).strip()
                sh, sm, eh, em = time

                events.append({
                    "day": current_day,
                    "title": title,
                    "start": (sh, sm),
                    "end": (eh, em)
                })

    return events

def create_ics(events):
    cal = "BEGIN:VCALENDAR\nVERSION:2.0\n"

    for e in events:
        start = datetime(2026, 3, e["day"], *e["start"])
        end = datetime(2026, 3, e["day"], *e["end"])

        cal += f"""BEGIN:VEVENT
UID:{uuid.uuid4()}
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start.strftime('%Y%m%dT%H%M%S')}
DTEND:{end.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{e["title"]}
END:VEVENT
"""

    cal += "END:VCALENDAR"
    return cal

def main():
    events = fetch_events()
    ics = create_ics(events)

    with open("calendar.ics", "w") as f:
        f.write(ics)

if __name__ == "__main__":
    main()
