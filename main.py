from __future__ import print_function
from importlib.resources import files

import io
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive']


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    print_names_ids_files(creds, 5)
    files = ['file1.txt', 'file2.txt']
    mime_types = ['text/plain', 'text/plain']  # .txt example
    upload_files(creds, '', files, mime_types)
    file_ids = [' ', '']
    downloaded_files_names = ['file1.txt', 'file2.txt']
    download_files(creds, file_ids, downloaded_files_names)


# Prints the names and ids of the first N files the user has access to.
def print_names_ids_files(creds, n):
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(
            pageSize=n, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # Errors from drive API.
        print(f'An error occurred: {error}')


# Upload files
def upload_files(creds, drive_folder_id, list_of_files, file_mime_types):
    try:
        service = build('drive', 'v3', credentials=creds)
        # specify the folder id to upload the files to
        folder_id = drive_folder_id
        # list all files to upload
        file_names = list_of_files
        # specify the mime type of your files
        mime_types = file_mime_types

        for file_name, mime_type in zip(file_names, mime_types):
            file_metada = {
                'name': file_name,
                'parents': [folder_id]
            }
            # specify the file path of your files
            media = MediaFileUpload(
                'C:/Users/username/.../{0}'.format(file_name), mimetype=mime_type)
            service.files().create(
                body=file_metada,
                media_body=media,
                fields='id'
            ).execute()
    except HttpError as error:
        print(f'An error occurred: {error}')


def download_files(creds, drive_files_ids, downloaded_file_names):
    try:
        service = build('drive', 'v3', credentials=creds)
        file_ids = drive_files_ids
        file_names = downloaded_file_names
        for file_id, file_name in zip(file_ids, file_names):
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fd=fh, request=request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print('PROGRESS {0}'.format(status.progress() * 100))
            fh.seek(0)
            # specify the folder to download the files
            with open(os.path.join('C:/Users/username/Downloads/...', file_name), 'wb') as f:
                f.write(fh.read())
                f.close()
    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
