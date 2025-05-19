import tkinter as tk
from tkinter import ttk

root = tk.Tk()

entry = ttk.Entry(root)
entry.pack()

entry.insert(0, "Initial text")
entry.mark_set("insert", 5) # Sets the insertion point after the 5th character

root.mainloop()