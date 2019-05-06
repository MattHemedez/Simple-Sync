import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
import io

SCOPES = ["https://www.googleapis.com/auth/drive.appdata", "https://www.googleapis.com/auth/drive.file"]


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
        response = self.service.files().list(spaces='appDataFolder',
                                             orderBy="name",
                                             fields='files(id, name, md5Checksum, webContentLink)',
                                             ).execute()

        # files_dict = self.service.files().list(corpora="user", orderBy="name",
        #                                 q="mimeType != 'application/vnd.google-apps.folder'",
        #                                 fields="files(name, md5Checksum, id, webContentLink)").execute()
        result = {}
        for file_info in response["files"]:
            result[file_info["name"]] = {"md5": file_info.get("md5Checksum", None),
                                         "file_id": file_info["id"],
                                         "d_link": file_info.get("webContentLink", None)}

        return result

    def get_file(self, file_ID: str, file_name: str):
        request = self.service.files().get_media(fileId="1mPuQUmR3Pyz9Ews1qI4zenJ-JRvifTrP")
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        return True

    def upload_file(self, file_name):
        file_metadata = {
            "name": file_name,
            "parents": ["appDataFolder"]
        }
        media = MediaFileUpload(file_name,
                                resumable=True)
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()
        print('File ID: %s' % file.get('id'))

    def delete_file(self, file_id):
        pass

    def print_file_id_list(self):
        file_list = self.get_info_on_files()
        for file_name, file_info in file_list.items():
            print(file_name, ":")
            print("\tmd5 Checksum: \t", file_info["md5"])
            print("\tFile ID: \t\t", file_info["file_id"])
            print("\tDownload Link: \t\t", file_info["d_link"])


if __name__ == "__main__":
    testApi = GoogleDriveApiHandler()
    # testApi.upload_file("test.txt")

    # """
    # Determine Files in appdata
    file_dict = testApi.get_info_on_files()
    for file_name, file_data in file_dict.items():
        print(file_name)
        for key, element in file_data.items():
            print("\t", key, ":", element)
    # """
    # testApi.get_file("https://drive.google.com/uc?id=1mPuQUmR3Pyz9Ews1qI4zenJ-JRvifTrP&export=download", "test1.txt")

