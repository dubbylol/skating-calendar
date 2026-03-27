import requests
from bs4 import BeautifulSoup
from datetime import datetime
import uuid
import re
import urllib3

# Fix SSL issue
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://www.ashlandskateland.com/calendar.html"

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

def parse_time(text):
    match = re.search(r'(\d{1,2})(:(\d{2}))?(am|pm)-(\d{1,2})(:(\d{2}))?(am|pm)', text, re.I)
    if not match:
        return None

    def convert(h, m, ap):
        h = int(h)
        m = int(m) if m else 0
        if ap.lower() == "pm" and h != 12:
            h += 12
        if ap.lower() == "am" and h == 12:
            h = 0
        return h, m

    sh, sm = convert(match.group(1), match.group(3), match.group(4))
    eh, em = convert(match.group(5), match.group(7), match.group(8))

    return sh, sm, eh, em

def main():
    html = requests.get(URL, verify=False).text
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n")

    lines = [clean(l) for l in text.split("\n") if l.strip()]

    events = []
    day = None

    for line in lines:
        if line.isdigit():
            day = int(line)
            continue

        if day:
            time = parse_time(line)
            if time:
                title = re.sub(r'\d.*', '', line).strip()
                sh, sm, eh, em = time

                start = datetime(2026, 3, day, sh, sm)
                end = datetime(2026, 3, day, eh, em)

                events.append(f"""BEGIN:VEVENT
UID:{uuid.uuid4()}
DTSTAMP:20260101T000000Z
DTSTART:{start.strftime('%Y%m%dT%H%M%S')}
DTEND:{end.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{title}
END:VEVENT""")

    cal = "BEGIN:VCALENDAR\nVERSION:2.0\n" + "\n".join(events) + "\nEND:VCALENDAR"

    with open("calendar.ics", "w") as f:
        f.write(cal)

if __name__ == "__main__":
    main()
