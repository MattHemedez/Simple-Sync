from tkinter import *
from tkinter import ttk, filedialog
from configure_file_handler import ConfigurationHandler
from pathlib import Path
from time import ctime
from os import startfile
from synchronizer import Synchronizer


IMG_DIR = Path("res/")


# Static Helper Functions
def convert_b_to_kb_str(num: int):
    return str(round(num / 1000.0)) + " KB"


def path_str_to_photo_image(path_str: str):
    path_str = Path(path_str).resolve()
    photo_img = PhotoImage(file=path_str)
    return photo_img


class SimplySyncGui:
    def __init__(self):
        self.conf_handler = ConfigurationHandler()
        self.sync_handler = Synchronizer(self.conf_handler.get_conf_entry("file_dir_path"))
        # self.sync_handler = "Testing. Delete this when done."

        self.root = Tk()
        # self.style = ttk.Style()
        # print(self.style.theme_names())
        # self.style.theme_use("xpnative")

        # Images
        self.img_reload_btn = path_str_to_photo_image("res/reload.png")
        self.img_settings_btn = path_str_to_photo_image("res/settings.png")
        self.img_logo = path_str_to_photo_image("res/512x512.png")

        # Gui Elements
        self.sync_dir = StringVar()
        self.sync_dir.set(Path(self.conf_handler.get_conf_entry("file_dir_path")).resolve())
        self.mainframe = ttk.Frame(self.root, padding="0 0 0 0")
        self.file_view = None
        self.init_gui_elements()

        self.refresh_file_view()

    def run(self):
        self.root.mainloop()

    def change_file_folder_path(self):
        new_dir = filedialog.askdirectory()
        if new_dir != "":
            self.conf_handler.change_conf_entry("file_dir_path", new_dir)
            self.conf_handler.save_conf()
            self.sync_dir.set(Path(self.conf_handler.get_conf_entry("file_dir_path")).resolve())
            self.refresh_file_view()
            self.sync_handler.set_file_dir_path(self.conf_handler.get_conf_entry("file_dir_path"))

    def on_upload_btn_click(self):
        self.sync_handler.upload()
        self.refresh_file_view()

    def on_download_btn_click(self):
        self.sync_handler.download()
        self.refresh_file_view()

    def on_file_double_click(self):
        selected_file = self.file_view.focus()
        startfile(Path(self.file_view.item(selected_file)["values"][3]))

    def refresh_file_view(self):
        self.file_view.delete(*self.file_view.get_children())
        for file_path in Path(self.sync_dir.get()).iterdir():
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
        self.root.title("Simply Sync")
        self.root.iconbitmap(IMG_DIR / "simply_sync.ico")
        self.root.geometry("350x400")

        # Main Window Configuration
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # Grid Configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.columnconfigure(1, weight=1)
        self.mainframe.rowconfigure(0, weight=0)
        self.mainframe.rowconfigure(1, weight=2)
        self.mainframe.rowconfigure(2, weight=1)

        # Style Section
        ttk.Style().configure("UploadButton.TButton", background="#72DDF7")
        ttk.Style().configure("DownloadButton.TButton", background="#C33C54")

        # tk Objects Initialization
        file_view_frame = Frame(self.mainframe)
        file_view_frame.grid(row=1, columnspan=2, sticky=(N, W, E, S), padx=2, pady=2)

        vsb = ttk.Scrollbar(file_view_frame)
        vsb.pack(side="right", fill="y")

        all_columns = ("Type", "Date modified", "Size", "Path")
        columns_to_display = all_columns[0:3]
        self.file_view = ttk.Treeview(file_view_frame,
                                      columns=columns_to_display,
                                      height=10,
                                      displaycolumns=columns_to_display,
                                      padding=[3, 3, 3, 3],
                                      selectmode="extended",
                                      yscrollcommand=vsb.set)
        vsb.config(command=self.file_view.yview)
        for column in columns_to_display:
            self.file_view.column(column=column, anchor="w", stretch=True)
            self.file_view.heading(column, anchor="w", text=column)
        self.file_view.column(column="#0", anchor="w", stretch=True)
        self.file_view.heading("#0", anchor="w", text="File Name")
        self.file_view.pack(side="left", fill="both")
        self.file_view.tag_configure("file", background="#98FB98")
        self.file_view.tag_bind("file", "<Double-Button-1>", self.on_file_double_click)

        ttk.Button(self.mainframe,
                   style="UploadButton.TButton",
                   text="Upload",
                   command=self.on_upload_btn_click).grid(column=0, row=2, sticky=(N, W, E, S))
        ttk.Button(self.mainframe,
                   style="DownloadButton.TButton",
                   text="Download",
                   command=self.on_download_btn_click).grid(column=1, row=2, sticky=(N, W, E, S))

        path_config_frame = Frame(self.mainframe)
        path_config_frame.grid(columnspan=2, row=0, sticky=(N, W, E, S))
        settings_btn_frame = Frame(path_config_frame, height=16, width=28)
        settings_btn_frame.pack(side="right", fill="y")

        ttk.Button(settings_btn_frame,
                   image=self.img_settings_btn,
                   command=self.change_file_folder_path).grid(column=0, row=0, sticky=(N, W, E, S))

        ttk.Button(settings_btn_frame,
                   image=self.img_reload_btn,
                   command=self.refresh_file_view).grid(column=1, row=0, sticky=(N, W, E, S))

        ttk.Label(path_config_frame, textvariable=self.sync_dir).pack(side="left", fill="y")


if __name__ == "__main__":
    myApp = SimplySyncGui()
    myApp.run()
