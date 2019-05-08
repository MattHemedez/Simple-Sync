from synchronizer import Synchronizer


class Console:
    def __init__(self):
        self.command = ""
        self.syncer = Synchronizer()

    def sync_test_file(self):
        self.syncer.download()
        print("Syncing finished...")

    def upload_test_file(self):
        self.syncer.upload()
        print("Everything is uploaded.")

    def reset_drive(self):
        self.syncer.reset_drive()

    def get_command(self):
        self.command = input_get_str("> ").lower()

    def list_files(self):
        file_names_list = self.syncer.get_drive_file_names()
        for i, file_name in enumerate(file_names_list, start=1):
            print(i, ":", file_name)

    def process_command(self):
        if self.command == "h":
            print_menu()
        elif self.command == "s":
            self.sync_test_file()
        elif self.command == "u":
            self.upload_test_file()
        elif self.command == "r":
            self.reset_drive()
        elif self.command == "l":
            self.list_files()
        elif self.command == "q":
            # Handled in outer function
            pass
        else:
            print("Command does not exist...")

    def run_command_prompt(self):
        print_start_message()
        while not self.command == "q":
            self.get_command()
            self.process_command()


"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


def input_get_str(prompt: str) -> str:
    result = input(prompt)
    return result


def print_start_message():
    print("Type h for a list of commands...")


def print_menu():
    menu = ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
            "u - uploads all files in sync folder\n"
            "s - Downloads all files in drive\n"
            "h - displays this menu\n"
            "r - deletes all files in drive\n"
            "l - lists all files in drive\n"
            "q - exits menu\n"
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(menu)


def run():
    my_console = Console()
    my_console.run_command_prompt()
    """Give user a command line interface to test Simple-Sync commands"""


if __name__ == "__main__":
    run()