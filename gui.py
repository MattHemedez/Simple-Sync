from tkinter import *
from tkinter import ttk
from synchronizer import Synchronizer


# Init
syncer = Synchronizer()


# Helper Functions
def upload_button():
    syncer.upload()


def download_button():
    syncer.download()


# Root Configuration
root = Tk()
root.title = "Simple Sync"

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
ttk.Label(mainframe, text="To be redone").grid(columnspan=2, sticky=(W, E))

ttk.Button(mainframe, style="UploadButton.TButton", text="Upload", command=upload_button).grid(column=0, row=1, sticky=(N, W, E, S))
ttk.Button(mainframe, style="DownloadButton.TButton", text="Download", command=download_button).grid(column=1, row=1, sticky=(N, W, E, S))

# Running the Program
root.mainloop()
