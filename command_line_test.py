def print_menu():
    print("""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
m - menu
h - help
r - reset
q - quit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """)


def print_start_message():
    print("Type m for a list of commands...")


def get_command():
    return input_get_str("> ")


def run_command_prompt():
    command = ""
    print_start_message()
    while not command == "q":
        command = get_command()


def input_get_str(prompt: str) -> str:
    result = input(prompt)
    return result


def run():
    run_command_prompt()
    """Give user a command line interface to test Simple-Sync commands"""


if __name__ == "__main__":
    run()