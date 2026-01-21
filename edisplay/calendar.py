from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from pprint import pprint

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from edisplay.secrets import get_secret

SCOPES = ["https://www.googleapis.com/auth/calendar.events.readonly"]


@dataclass
class Event:
    summary : str
    description : str
    start : datetime
    end : datetime
    location: str


def get_events(from_date, to_date, max_results=4):
  creds = Credentials.from_service_account_file('google_credentials_calendar.json', scopes=SCOPES)

  try:
    service = build('calendar', 'v3', credentials=creds)

    events_result = (
        service.events()
        .list(
            calendarId=get_secret('Calendar', 'CalendarId'),
            timeMin=from_date,
            timeMax=to_date,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime',
        )
        .execute()
    )
    events = events_result.get('items', [])
    return [Event(
        summary=e['summary'], 
        description=e.get('description'), 
        start=datetime.fromisoformat(e['start']['dateTime']), 
        end=datetime.fromisoformat(e['end']['dateTime']),
        location=e.get('location'))
        for e in events]

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
    now = datetime.now(tz=timezone.utc)
    tomorrow = now + timedelta(days=1)
    from_date = now.isoformat()
    to_date = tomorrow.isoformat()
    pprint(get_events(from_date, to_date))
