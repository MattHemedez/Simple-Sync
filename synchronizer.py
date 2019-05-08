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
        self.drive_api = GoogleDriveApiHandler()

    def upload(self):
        """
        Upload a single folder with files. Cannot be larger than
        remaining Google Drive space. Cannot go through more folders.
        Deletes all files in Google Drive that don't have file names in
        file folder.
        """

        paths_of_files = [str(file_path_obj) for file_path_obj in FILES_DIR.iterdir()]
        names_of_files = [file_path_obj.name for file_path_obj in FILES_DIR.iterdir()]

        for file_path in paths_of_files:
            self.drive_api.upload_file(file_path)

        files_dict = self.drive_api.get_info_on_files()

        for file_id, file_info in files_dict.items():
            if file_info["name"] not in names_of_files:
                self.drive_api.delete_file(file_id)

    def download(self):
        """
        Download files from Google Drive into files folder.
        Delete all files not found in Google Drive folder.
        """
        names_of_files_local = [file_path_obj.name for file_path_obj in FILES_DIR.iterdir()]

        files_dict = self.drive_api.get_info_on_files()

        names_of_files_drive = []
        for file_id, file_info in files_dict.items():
            names_of_files_drive.append(file_info["name"])
            file_path = str(FILES_DIR / file_info["name"])
            self.drive_api.download_file(file_id, file_path)

        for file_name_local in names_of_files_local:
            if file_name_local not in names_of_files_drive:
                self.delete_file_computer(file_name_local)

    def get_drive_file_names(self):
        file_dict = self.drive_api.get_info_on_files()
        return [file_info["name"] for file_info in file_dict.values()]

    def does_drive_file_exist(self, file_name):
        if self.drive_api.get_file_id_if_exists() is None:
            return False
        return True

    def delete_file_drive(self, file_name):
        pass

    def delete_file_computer(self, file_name):
        print("Deleting File:" + file_name)
        file_path = FILES_DIR / file_name
        file_path.unlink()
        return True

    def delete_file_both(self, file_name):
        pass

    def reset_drive(self):
        self.drive_api.reset_all_files()

    def upload_file(self, file_name):
        file_path = str(FILES_DIR / file_name)
        self.drive_api.upload_file(file_path)

    def download_file(self, file_name):
        file_id = self.drive_api.get_file_id_if_exists(file_name)
        file_path = str(FILES_DIR / file_name)
        self.drive_api.download_file(file_id, file_path)


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
        if len(result) == 0:
            return None
        return result[0]["id"]

    def download_file(self, file_id: str, file_path: str):
        file_name = Path(file_path).name
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        with open(file_path, "wb") as out:
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

