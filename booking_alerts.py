import os
import requests
import hashlib
from icalendar import Calendar

AIRBNB_ICAL_URL = os.environ["AIRBNB_ICAL_URL"]
BOOKING_ICAL_URL = os.environ["BOOKING_ICAL_URL"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

seen = set()

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg})

def get_events(url, source):
    cal = Calendar.from_ical(requests.get(url).text)
    events = []
    for e in cal.walk():
        if e.name == "VEVENT":
            start = str(e.get("dtstart").dt)
            end = str(e.get("dtend").dt)
            summary = str(e.get("summary"))
            key = hashlib.md5(f"{start}{end}{summary}".encode()).hexdigest()
            events.append((key, source, start, end, summary))
    return events

def main():
    global seen
    events = []
    events += get_events(AIRBNB_ICAL_URL, "Airbnb")
    events += get_events(BOOKING_ICAL_URL, "Booking")

    for key, source, start, end, summary in events:
        if key not in seen:
            seen.add(key)
            send(f"🏡 New booking ({source})\n{summary}\n{start} → {end}")

import time

if __name__ == "__main__":
    while True:
        main()
        time.sleep(300)  # check every 5 minutes
