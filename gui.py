from tkinter import *
from tkinter import ttk
from synchronizer import Synchronizer
from configure_file_handler import ConfigurationHandler
from pathlib import Path
from time import ctime
from os import startfile


# Init
configuration_handler = ConfigurationHandler()
syncer = Synchronizer(configuration_handler.get_conf_entry("file_dir_path"))
# syncer = "Testing. Delete this when done."


# Constants
FILE_DIR = Path(configuration_handler.get_conf_entry("file_dir_path"))
IMG_DIR = Path("res/")


# Helper Functions
def upload_button():
    syncer.upload()


def download_button():
    syncer.download()


def on_file_double_click(pos):
    selected_file = file_view.focus()
    startfile(Path(file_view.item(selected_file)["values"][3]))


def convert_B_to_KB_str(num: int):
    return str(round(num / 1000.0)) + " KB"


def refresh_file_view(tree_view: ttk.Treeview):
    for file_path in FILE_DIR.iterdir():
        file_name = file_path.name
        tree_view.insert("", "end", file_name,
                         tags=("file"),
                         text=file_name,
                         values=(file_path.suffix[1:],
                                 ctime(file_path.stat().st_mtime),
                                 convert_B_to_KB_str(file_path.stat().st_size),
                                 file_path))


# Root Configuration
root = Tk()
root.title("Simple Sync")
root.iconbitmap(IMG_DIR / "simple_sync.ico")

# Main Window Configuration
mainframe = ttk.Frame(root, padding="0 0 0 0")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

# Re-drawable Configuration
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

mainframe.columnconfigure(0, weight=1)
mainframe.columnconfigure(1, weight=1)
mainframe.rowconfigure(0, weight=2)
mainframe.rowconfigure(1, weight=1)

# Style Section
ttk.Style().configure("UploadButton.TButton", relief="flat", background="#72DDF7")
ttk.Style().configure("DownloadButton.TButton", relief="flat", background="#C33C54")

# tk Objects Initialization
all_columns = ("Type", "Date modified", "Size", "Path")
columns_to_display = all_columns[0:3]
file_view = ttk.Treeview(mainframe, columns=columns_to_display, height=10, displaycolumns=columns_to_display,
                         padding=[3, 3, 3, 3], selectmode="extended")
for column in columns_to_display:
    file_view.column(column=column, anchor="w", stretch=True)
    file_view.heading(column, anchor="w", text=column)
file_view.column(column="#0", anchor="w", stretch=True)
file_view.heading("#0", anchor="w", text="File Name")
file_view.grid(columnspan=2, sticky=(N, W, E, S))
file_view.tag_configure("file", background="#72DDF7")
file_view.tag_bind("file", "<Double-Button-1>", on_file_double_click)  # the item clicked can be found via tree.focus()

ttk.Button(mainframe, style="UploadButton.TButton", text="Upload", command=upload_button).grid(column=0, row=1, sticky=(N, W, E, S))
ttk.Button(mainframe, style="DownloadButton.TButton", text="Download", command=download_button).grid(column=1, row=1, sticky=(N, W, E, S))

# Running the Program
refresh_file_view(file_view)
root.mainloop()

