import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']


class Synchronizer:
    def __init__(self):
        pass

    def upload(self):
        """
        Upload a single folder with files. Cannot be larger than
        remaining Google Drive space. Cannot go through more folders.
        """
        pass

    def download(self):
        """
        Download folder reserved for single sync.
        """
        pass

    def get_drive_file_names_in_dir(self, dir_name):
        pass

    def does_drive_file_exist(self, file_name):
        pass

    def delete_drive_file(self, file_name):
        pass

    def upload_drive_file(self, file_name):
        pass

    def delete_file(self, file_name):
        pass

    def download_file(self, file_name):
        pass


class GoogleDriveApiHandler:
    def __init__(self):
        self.creds = None
        self.get_credentials()
        self.service = build('drive', 'v3', credentials=self.creds)

    def get_credentials(self):
        self.creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle') and os.path.getsize('token.pickle') > 0:
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def get_info_on_files(self):
        temp = self.service.files().list(corpora="user", orderBy="name",
                                         q="mimeType != 'application/vnd.google-apps.folder'",
                                         fields="files(name, md5Checksum)").execute()
        result = {}
        for file_info in temp["files"]:
            result[file_info["name"]] = file_info.get("md5Checksum", None)

        return result

    def download_files


if __name__ == "__main__":
    myGoogleApiHandler = GoogleDriveApiHandler()
    myGoogleApiHandler.get_files()
