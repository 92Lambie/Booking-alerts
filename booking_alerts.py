import os
import time
import requests
import hashlib
from icalendar import Calendar

AIRBNB_ICAL_URL = os.environ["AIRBNB_ICAL_URL"]
BOOKING_ICAL_URL = os.environ["BOOKING_ICAL_URL"]
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

seen = set()
first_run = True


def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        json={"chat_id": TELEGRAM_CHAT_ID, "text": msg},
        timeout=30,
    )


def get_events(url, source):
    cal = Calendar.from_ical(requests.get(url, timeout=30).text)
    events = []

    for e in cal.walk():
        if e.name != "VEVENT":
            continue

        start = str(e.get("dtstart").dt)
        end = str(e.get("dtend").dt)
        summary = str(e.get("summary", "")).strip()

        key = hashlib.md5(f"{source}|{start}|{end}|{summary}".encode()).hexdigest()
        events.append((key, source, start, end))

    return events


def main():
    global first_run
    global seen

    events = []
    events += get_events(AIRBNB_ICAL_URL, "Airbnb")
    events += get_events(BOOKING_ICAL_URL, "Booking.com")

    current_keys = set()

    for key, source, start, end in events:
        current_keys.add(key)

        if first_run:
            seen.add(key)
            continue

        if key not in seen:
            send(f"🏡 New booking\n{source}\n{start} → {end}")
            seen.add(key)

    seen = current_keys
    first_run = False


if __name__ == "__main__":
    while True:
        main()
        time.sleep(300)  # check every 5 minutes
