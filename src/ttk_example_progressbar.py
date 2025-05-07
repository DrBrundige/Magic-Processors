import tkinter as tk
from tkinter import filedialog
import os

def open_file_explorer():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askdirectory()
    if file_path:
        os.startfile(file_path)

open_file_explorer()