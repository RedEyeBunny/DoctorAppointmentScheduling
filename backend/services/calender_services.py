from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime

def create_calendar_event(email, slot_time):
    credentials = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/calendar"]
    )

    service = build("calendar", "v3", credentials=credentials)

    event = {
        "summary": "Doctor Appointment",
        "start": {"dateTime": slot_time, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": slot_time, "timeZone": "Asia/Kolkata"},
        "attendees": [{"email": email}],
    }

    service.events().insert(calendarId="primary", body=event).execute()
