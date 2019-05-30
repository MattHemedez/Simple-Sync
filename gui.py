from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from synchronizer import Synchronizer
from configure_file_handler import ConfigurationHandler
from pathlib import Path
from time import ctime
from os import startfile


IMG_DIR = Path("res/")


# Static Helper Functions
def convert_b_to_kb_str(num: int):
    return str(round(num / 1000.0)) + " KB"


class SimplySyncGui:
    def __init__(self):
        self.conf_handler = ConfigurationHandler()
        self.sync_handler = Synchronizer(self.conf_handler.get_conf_entry("file_dir_path"))
        # self.sync_handler = "Testing. Delete this when done."

        self.sync_dir = Path(self.conf_handler.get_conf_entry("file_dir_path"))

        # Gui Elements
        self.root = Tk()
        self.mainframe = ttk.Frame(self.root, padding="0 0 0 0")
        self.file_view = None
        self.menu_bar = Menu(self.root)
        self.settings_menu = Menu(self.menu_bar, tearoff=0)
        self.init_gui_elements()

        self.refresh_file_view()

    def run(self):
        self.root.mainloop()

    def change_file_folder_path(self):
        new_dir = filedialog.askdirectory()
        self.conf_handler.change_conf_entry("file_dir_path", new_dir)
        self.conf_handler.save_conf()
        self.sync_dir = Path(self.conf_handler.get_conf_entry("file_dir_path"))
        self.refresh_file_view()

    def upload_button(self):
        self.sync_handler.upload()

    def download_button(self):
        self.sync_handler.download()

    def on_file_double_click(self):
        selected_file = self.file_view.focus()
        startfile(Path(self.file_view.item(selected_file)["values"][3]))

    def refresh_file_view(self):
        self.file_view.delete(*self.file_view.get_children())
        for file_path in self.sync_dir.iterdir():
            file_name = file_path.name
            self.file_view.insert("", "end", file_name,
                                  tags=("file"),
                                  text=file_name,
                                  values=(file_path.suffix[1:],
                                          ctime(file_path.stat().st_mtime),
                                          convert_b_to_kb_str(file_path.stat().st_size),
                                          file_path))

    def init_gui_elements(self):
        # Root Configuration
        self.root.title("Simple Sync")
        self.root.iconbitmap(IMG_DIR / "simple_sync.ico")

        # Main Window Configuration
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # Re-drawable Configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.rowconfigure(0, weight=2)
        self.mainframe.rowconfigure(1, weight=1)

        # Style Section
        ttk.Style().configure("UploadButton.TButton", relief="flat", background="#72DDF7")
        ttk.Style().configure("DownloadButton.TButton", relief="flat", background="#C33C54")

        # tk Objects Initialization
        all_columns = ("Type", "Date modified", "Size", "Path")
        columns_to_display = all_columns[0:3]
        self.file_view = ttk.Treeview(self.mainframe,
                                      columns=columns_to_display,
                                      height=10,
                                      displaycolumns=columns_to_display,
                                      padding=[3, 3, 3, 3],
                                      selectmode="extended")
        for column in columns_to_display:
            self.file_view.column(column=column, anchor="w", stretch=True)
            self.file_view.heading(column, anchor="w", text=column)
        self.file_view.column(column="#0", anchor="w", stretch=True)
        self.file_view.heading("#0", anchor="w", text="File Name")
        self.file_view.grid(columnspan=2, sticky=(N, W, E, S))
        self.file_view.tag_configure("file", background="#72DDF7")
        self.file_view.tag_bind("file", "<Double-Button-1>", self.on_file_double_click)

        ttk.Button(self.mainframe,
                   style="UploadButton.TButton",
                   text="Upload",
                   command=self.upload_button).grid(column=0, row=1, sticky=(N, W, E, S))
        ttk.Button(self.mainframe,
                   style="DownloadButton.TButton",
                   text="Download",
                   command=self.download_button).grid(column=1, row=1, sticky=(N, W, E, S))

        self.settings_menu.add_command(label="Change Syncing Folder Path", command=self.change_file_folder_path)

        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.root.config(menu=self.menu_bar)


if __name__ == "__main__":
    myApp = SimplySyncGui()
    myApp.run()
