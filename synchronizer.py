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


class Synchronizer:
    def __init__(self, file_dir_path="files/"):
        """
        Initialize Google Drive API handler. Determine folder to be used for file syncing features.

        :param folder_path: str representing path to the directory containing files to be synced.
        """
        self.drive_api = GoogleDriveApiHandler()
        self.dir_path = Path(file_dir_path)

    def upload(self):
        """
        Upload a single folder with files. Cannot be larger than remaining Google Drive space. Cannot go through
        more folders. Deletes all files in Google Drive that don't have file names in file folder.

        :return: None
        """

        paths_of_files = [str(file_path_obj) for file_path_obj in self.dir_path.iterdir()]
        names_of_files = [file_path_obj.name for file_path_obj in self.dir_path.iterdir()]

        for file_path in paths_of_files:
            self.drive_api.upload_file(file_path)

        files_dict = self.drive_api.get_info_on_files()

        for file_id, file_info in files_dict.items():
            if file_info["name"] not in names_of_files:
                self.drive_api.delete_file(file_id)

    def download(self):
        """
        Download files from Google Drive into files folder. Delete all files not found in Google Drive folder.

        :return: None
        """
        names_of_files_local = [file_path_obj.name for file_path_obj in self.dir_path.iterdir()]

        files_dict = self.drive_api.get_info_on_files()

        names_of_files_drive = []
        for file_id, file_info in files_dict.items():
            names_of_files_drive.append(file_info["name"])
            file_path = str(self.dir_path / file_info["name"])
            self.drive_api.download_file(file_id, file_path)

        for file_name_local in names_of_files_local:
            if file_name_local not in names_of_files_drive:
                self.delete_file_computer(file_name_local)

    def get_drive_file_names(self):
        """
        List all files in Google Drive.

        :return: None
        """
        file_dict = self.drive_api.get_info_on_files()
        return [file_info["name"] for file_info in file_dict.values()]

    def does_drive_file_exist(self, file_name: str):
        """
        Determine if file with given file name exists within Google Drive.

        :param file_name: str represents file name in Google Drive to search for.
        :return: None
        """
        if self.drive_api.get_file_id_if_exists(file_name) is None:
            return False
        return True

    def delete_file_drive(self, file_name):
        pass

    def delete_file_computer(self, file_name: str):
        """
        Delete file from local machine in the designated file folder on the local machine.

        :param file_name: str represents file name to search for and delete in local file storage.
        :return: True if file is deleted
        """
        print("Deleting File:" + file_name)
        file_path = self.dir_path / file_name
        file_path.unlink()
        return True

    def delete_file_both(self, file_name):
        pass

    def reset_drive(self):
        """
        Deletes all files stored in Google Drive.

        :return: None
        """
        self.drive_api.reset_all_files()

    def upload_file(self, file_name: str):
        """
        Download file from Google Drive based on file name.

        :param file_name: str represents file to download from Google Drive.
        :return: None
        """
        file_path = str(self.dir_path / file_name)
        self.drive_api.upload_file(file_path)

    def download_file(self, file_name: str):
        """
        Download file one file from Google Drive specified by file name.

        :param file_name: str represents file to download from Google Drive.
        :return: None
        """
        file_id = self.drive_api.get_file_id_if_exists(file_name)
        file_path = str(self.dir_path / file_name)
        self.drive_api.download_file(file_id, file_path)

    def upload_clipboard(self):
        pass

    def download_clipboard(self):
        pass


class GoogleDriveApiHandler:
    def __init__(self):
        """
        Initialize Google Drive API by retrieving credentials and building service api.
        """
        self.creds = None
        self.get_credentials()
        self.service = build('drive', 'v3', credentials=self.creds)

    def get_credentials(self):
        """
        Retrieves stored user credentials if one exists or prompts User to authorize application.

        :return: None
        """
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
        """
        Retrieve current Google Drive info on stored files. List file id, file name, md5Checksum, and deletion status.

        :return: dict indexed by unique google drive file id. Element is a dict that lists file information.
        """
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
        """
        Return a file id if it currently exists in Google Drive or None otherwise. If duplicates exist then return
        arbitrary file id with file name.

        :param file_name: Name of the file to look for.
        :return: None if no file exists. str that is the file id if it exists.
        """
        query = "name='" + file_name + "'"
        response = self.service.files().list(spaces='appDataFolder',
                                             fields="files(id)",
                                             q=query).execute()
        result = response.get("files", None)
        if len(result) == 0:
            return None
        return result[0]["id"]

    def download_file(self, file_id: str, file_path: str):
        """
        Download file with file id and save it to given file path. File path must be a proper file path, else undefined
        behavior occurs.

        :param file_id: str represents the Google Drive file id.
        :param file_path: str that represents the file path to save the downloaded file to.
        :return: True if it succeeds or throw error if not.
        """
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
        """
        Download all files within Google Drive folder. Give each file name found in Google Drive. Duplicates are not
        considered and will result in an overwrite.

        :return: None
        """
        file_dict = self.get_info_on_files()
        for file_id, file_info in file_dict.items():
            self.download_file(file_id, file_info["name"])

    def upload_file(self, file_path: str):
        """
        Upload file located at the given file path to Google Drive. Replace file with name if exists in Google Drive.

        :param file_path: str that represents path to the file to upload.
        :return: None
        """
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

    def delete_file(self, file_id: str):
        """
        Delete file in Google Drive given file id.

        :param file_id: str represents file id of file in Google Drive.
        :return: None
        """
        self.service.files().delete(fileId=file_id).execute()

    def reset_all_files(self):
        """
        Delete all files in this apps Google Drive folder.

        :return: None
        """
        file_dict = self.get_info_on_files()
        for file_id in file_dict.keys():
            self.delete_file(file_id)

    def _print_file_id_list(self):
        """
        Debug function to list all file ids within Google Drive folder. Prints out file id, checksum, and file name for
        each function.

        :return: None
        """
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
