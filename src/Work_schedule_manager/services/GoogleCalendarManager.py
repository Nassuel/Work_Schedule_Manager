import datetime
import os
from typing import Any, List, Union

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from utils.store import logger, EventType

class GoogleCalendarService():
    SCOPES = [
        'https://www.googleapis.com/auth/calendar'
    ]
    def __init__(self) -> None:
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_path = './creds/token.json'
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './creds/credentials.json', self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        self.creds = creds

    def get_creds(self):
        return self.creds

class GoogleEvent():
    """
        https://developers.google.com/calendar/api/v3/reference/events
    """
    EVENTTYPE = 'google_calendar'
    def __init__(self, creds, start_time: Union[str, datetime.datetime], subject: str, end_time: Union[str, datetime.datetime], location: str, recipients: List[str], attachments: List[str], body: str, body_fields=None) -> None:
        self.creds = creds
        event = {}
        event['description'] = body if body_fields is None else body.format(**body_fields)

        self.event = event.update({
            'summary': subject,
            'location': location,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Los_Angeles',
            },
            # 'recurrence': [
            #     'RRULE:FREQ=DAILY;COUNT=2'
            # ],
            'attendees': [
                {'email': email for email in recipients}
            ],
            'reminders': {
                'useDefault': True,
                # 'overrides': [
                #     {'method': 'email', 'minutes': 24 * 60},
                #     {'method': 'popup', 'minutes': 10},
                # ],
            },
        })

    def __str__(self) -> str:
        return str(self.event)

    def save_and_send(self) -> None:
        """
        Each event has the attribute of sending itself, called by event terminal
        """
        event_execution = self.event_queued.execute()
        print(f"Event created: {event_execution.get('htmlLink')}")

    def create_event(self) -> Any:
        """
        Create an event on my 'primary' calendar
        Refer to the Python quickstart on how to setup the environment:
        https://developers.google.com/calendar/quickstart/python
        Change the scope to 'https://www.googleapis.com/auth/calendar' and delete any
        stored credentials.
        https://developers.google.com/calendar/api/guides/create-events
        """
        try:
            if self.creds is not None: 
                service = build('calendar', 'v3', credentials=self.creds)
            else:
                raise ValueError('Creds were not set properly')

            self.event_queued = service.events().insert(calendarId='primary', body=self.event)

        except HttpError as error:
            print(f"An error occurred: {error}")