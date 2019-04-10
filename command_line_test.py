class Console:
    def __init__(self):
        self.command = ""

    def reset(self):
        self.command = ""

    def get_command(self):
        self.command = input_get_str("> ")

    def process_command(self):
        if self.command == "m":
            print_menu()
        elif self.command == "h":
            print_start_message()
        elif self.command == "r":
            pass
        elif self.command == "q":
            # Handled in outer function
            pass

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
    print("Type m for a list of commands...")


def print_menu():
    menu = ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
            "m - menu\n"
            "h - help\n"
            "r - reset\n"
            "q - quit\n"
            "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print(menu)


def run():
    my_console = Console()
    my_console.run_command_prompt()
    """Give user a command line interface to test Simple-Sync commands"""


if __name__ == "__main__":
    run()