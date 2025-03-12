import time
from datetime import datetime
import pytz
import json
import tempfile
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import google.auth
import google.auth.transport.requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv
from googleapiclient.http import MediaFileUpload
import python_to_postgres as Postgres
import os
from datetime import timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv(".env")


def _account_identifier(reddit_query):
    tiktok_account = None
    youtube_account = f'sensitive/{reddit_query}_creds.json'
    token = f'sensitive/tokens/{reddit_query}_tokens.json'

    if reddit_query == "AmITheAsshole":
        tiktok_account = 'TBD'
    elif reddit_query == "Advice":
        tiktok_account = 'TBD'

    return {"youtube": youtube_account,
            "tiktok": tiktok_account,
            "token": token}


class Video:
    def __init__(self, tiktok_clips, tiktok_account, youtube):
        self.data = tiktok_clips
        # self.video_id = self.upload_video(youtube)
        self.tiktok_account = tiktok_account
        # self.subtitles = self.grab_subtitles(youtube)

    def upload_file_to_drive(self):
        credentials = service_account.Credentials.from_service_account_file('sensitive/service_acc.json')
        service = build('drive', 'v3', credentials=credentials)

        upload_ids = []
        # files = self.apply_split()
        for idx, video in enumerate(files, start=1):
            file_metadata = {
                'name': f'{self.data["Id"]}_part-{idx}',  # Name of the file to display in Google Drive
                'parents': ['1NRcYl8a6LoJRwG1wenGXiwFYurqG2QDM']  # Optional, specify folder in which to upload
            }

            media = MediaFileUpload(video, mimetype='video/mp4')  # Adjust mimetype if needed

            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            service.permissions().create(
                fileId=uploaded_file.get('id'),
                body={
                    'role': 'reader',
                    'type': 'anyone'  # Or 'user' if you want specific access only
                }
            ).execute()
            upload_ids.append(uploaded_file.get('id'))

        return upload_ids

    def download_to_hard_drive(self):
        hard_drive = os.path.abspath("/Volumes/Rotimi's_Disk/TikTok")
        folder = os.path.join(hard_drive, self.data['Title'])
        files = self.apply_split()
        for idx, video in enumerate(files, start=1):
            with open(f"{folder}/part-{idx}", 'wb') as video_file:
                video_file.write(video)

    def create_calendar_event(self):
        CLIENT_SECRET_FILE = "sensitive/service_acc.json"
        calendar_id = 'c_56be1da10246a154b6acb8ae9d62e18b79acf7dccfa6b1c2344732f5a8c7d1ce@group.calendar.google.com'
        email = os.environ.get("BUSINESS_EMAIL")
        api_key = os.environ.get("CALENDER_API_KEY")
        now = datetime.now(pytz.utc)
        fifteen_mins = now + timedelta(minutes=15)
        credentials = service_account.Credentials.from_service_account_file(
            CLIENT_SECRET_FILE,
            scopes=['https://www.googleapis.com/auth/calendar',
                    'https://www.googleapis.com/auth/calendar.events'],
            subject=email
        )

        service = build('calendar', 'v3', credentials=credentials)
        file_ids = self.upload_file_to_drive()
        date = self.data['upload time'] + timedelta(minutes=15)
        event = {
            'id': self.data["Id"],
            'summary': 'New Video to Upload',
            'location': self.tiktok_account,
            'description': f'https://drive.google.com/file/d/{file_ids[0]}/view & https://drive.google.com/file/d/{file_ids[1]}/view',
            'start': {
                'dateTime': fifteen_mins.isoformat().replace("+00:00", "Z"),
                'timeZone': 'GMT+00:00',
            },
            # 'end': {
            #     'dateTime': date.isoformat() + 'Z',
            #     'timeZone': 'GMT+01:00',
            # },
            'attendees': [
                {'email': f'{email}'}
            ],
            'attachments': [
                {
                    'fileUrl': f'https://drive.google.com/file/d/{file_ids[0]}/view',
                    'title': f'{self.data["Id"]}_video_part-1'
                },
                {
                    'fileUrl': f'https://drive.google.com/file/d/{file_ids[1]}/view',
                    'title': f'{self.data["Id"]}_video_part-2'
                }
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

        service.events().insert(calendarId=calendar_id, body=event, sendUpdates='all', key=api_key).execute()

        print('success')

    def upload_to_database(self):
        """
        Upload the story, gender, subtitles, and final video file paths to the Postgres database.

        """

        postgres_handler_init = Postgres.PGHandler("reddit_data")
        postgres_handler_init.insert_to_table(self.data["Id"], self.data["subreddit query"], self.data["Title"],
                                              self.data["Url"], "now()", "now()", None,
                                              self.data['Author'])
