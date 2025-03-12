import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build


def create_calendar_event(upload_time,
                          client_user_email,
                          reddit_id,
                          tiktok_account,
                          video_upload_info

                          ):
    CLIENT_SECRET_FILE = "../FalseFiles/service_acc_creds.json"
    calendar_id = os.environ.get("CALENDER_ID")
    API_KEY = os.environ.get("CALENDER_API_KEY")
    email = os.environ.get("BUSINESS_EMAIL")

    credentials = service_account.Credentials.from_service_account_file(
        CLIENT_SECRET_FILE,
        scopes=['https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/admin.directory.resource.calendar',
                'https://www.googleapis.com/auth/calendar.events'],
        subject=email
    )

    service = build('calendar', 'v3', credentials=credentials)

    event = {
        'id': reddit_id,
        'summary': 'New Video to Upload',
        'location': tiktok_account,
        'description': video_upload_info,
        'start': {
            'dateTime': upload_time,
            'timeZone': 'GMT+01:00',
        },
        'end': {
            'dateTime': upload_time + timedelta(minutes=15),
            'timeZone': 'GMT+01:00',
        },
        'attendees': [
            {'email': f'{client_user_email}'}
        ],

        'transparency': 'opaque',
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 60},
                {'method': 'popup', 'minutes': 15},
            ],
        },
    }

    service.events().insert(calendarId=calendar_id, body=event, sendUpdates='all', key=API_KEY).execute()


def convert_time_then_add(date, time, duration):
    datetime_str = f"{date}T{time}:00"
    duration_hours = duration
    start_time = datetime.fromisoformat(datetime_str)
    added_time = start_time + timedelta(hours=duration_hours)
    end_time = added_time.isoformat()
    return start_time.isoformat(), end_time
