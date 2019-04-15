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


if __name__ == "__main__":
    print("There is no test in this file.")
