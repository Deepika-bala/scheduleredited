from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']


def book_timeslot(event_description, booking_time, input_email):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # --------------------- Manipulating Booking Time ----------------------------
    start_time = str(datetime.datetime.now())[:10] + 'T' + booking_time + ':00+08:00'
    end_time = str(datetime.datetime.now())[:10] + 'T' + str(int(booking_time[:2]) + 1) + ':00:00+00:00'

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Booking a time slot....')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    if not events:
        event = {
            'summary': 'book an event',
            'location': 'madurai',
            'description': str(event_description) + 'with Madurai Startups',
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Singapore',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Singapore',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=1'
            ],
            'attendees': [
                {'email': '625001in@gmail.com'},
                {'email': str(input_email)},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return True

    else:
        # --------------------- Check if there are any similar start time ---------------------
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            if start == start_time:
                print('Already book....')
                return False
        # -------------------- Break out of for loop if there are no apppointment that has the same time ----------
        """event = {
            'summary': 'book an event',
            'location': 'Singapore',
            'description': str(event_description) + 'with Madurai Startups',
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Singapore',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Singapore',
            },
            'recurrence': [
                'RRULE:FREQ=DAILY;COUNT=1'
            ],
            'attendees': [
                {'email': '625001in@gmail.com'},
                {'email': str(input_email)},
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return True"""


if __name__ == '__main__':
    input_email = 'test@gmail.com'
    booking_time = '14:00'
    result = book_timeslot('event', booking_time, input_email)