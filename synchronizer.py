import pickle
import os.path
import io
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive.appdata", "https://www.googleapis.com/auth/drive.file"]
FILES_DIR = Path("files/")


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
                                             fields='files(id, name, md5Checksum, trashed)',
                                             q="mimeType != 'application/vnd.google-apps.folder'"
                                             ).execute()

        result = {}
        for file_info in response["files"]:
            result[file_info["id"]] = {"md5": file_info.get("md5Checksum", None),
                                         "name": file_info["name"],
                                         "trashed": file_info["trashed"]}

        return result

    def get_file_id_if_exists(self, file_name: str) -> str:
        query = "name='" + file_name + "'"
        response = self.service.files().list(spaces='appDataFolder',
                                             fields="files(id)",
                                             q=query).execute()
        result = response.get("files", None)
        if result is None:
            return result
        return result[0]["id"]

    def download_file(self, file_id: str, file_name: str):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        with open(file_name, "wb") as out:
            out.write(fh.getvalue())

        return True

    def download_all_files(self):
        file_dict = self.get_info_on_files()
        for file_id, file_info in file_dict.items():
            self.download_file(file_id, file_info["name"])

    def upload_file(self, file_path):
        file_name = Path(file_path).name
        file_id = self.get_file_id_if_exists(file_name)

        file_metadata = {
            "name": file_name,
            "parents": ["appDataFolder"]
        }

        media = MediaFileUpload(file_path,
                                resumable=True)
        if file_id is None:
            file = self.service.files().create(body=file_metadata,
                                               media_body=media,
                                               fields='id').execute()
        else:
            file = self.service.files().update(fileId=file_id,
                                               media_body=media,
                                               fields='id').execute()
        # print('File ID: %s' % file.get('id'))

    def delete_file(self, file_id):
        response = self.service.files().delete(fileId=file_id).execute()

    def reset_all_files(self):
        file_dict = self.get_info_on_files()
        for file_id in file_dict.keys():
            self.delete_file(file_id)

    def print_file_id_list(self):
        file_list = self.get_info_on_files()
        for file_id, file_info in file_list.items():
            print(file_id, ":")
            print("\tmd5 Checksum: \t", file_info["md5"])
            print("\tFile_Name: \t\t", file_info["name"])


if __name__ == "__main__":
    testApi = GoogleDriveApiHandler()
    # testApi.download_file("1AsKvzyKkqhQNaugGD32Xks5UgdsBi8q_thi00knvEvpAtxG9qg", str(FILES_DIR / "test5.txt"))
    # testApi.upload_file(str(FILES_DIR / "test.txt"))
    # testApi.reset_all_files()
    # testApi.delete_file("1p5FjF1imMqoSqBR5PD0xlIT10P8ffMRm3vzDFUAoHf04DFRNwA")

    testApi.print_file_id_list()
    # testApi.get_file("https://drive.google.com/uc?id=1mPuQUmR3Pyz9Ews1qI4zenJ-JRvifTrP&export=download", "test1.txt")

