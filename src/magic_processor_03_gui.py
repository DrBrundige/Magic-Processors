import tkinter as tk
from tkinter import ttk, filedialog
import os
from bulk_data_import import controller_get_sorted_data
from magic_processor_03 import new_controller_process_cards_from_file


class App(ttk.Frame):
	# calendar = None
	import_match_fields = 0

	# exporters = {}

	def __init__(self, master):
		super().__init__(master)
		self.pack()

		# window = tk.Tk()
		frm = ttk.Frame(master, padding=20, name="main_frame")

		ttk.Label(frm, text="Filename").grid(column=0, row=0, padx=10, pady=5)
		ttk.Entry(frm, name="txt_filename").grid(column=0, row=1, padx=10, pady=5)
		ttk.Button(frm, text="Search", command=self.get_main_file).grid(column=1, row=1, padx=0, pady=10)

		ttk.Label(frm, text="Match fields").grid(column=0, row=2, padx=10, pady=5)
		ttk.Entry(frm, name="txt_match").grid(column=0, row=3, padx=10, pady=5)
		ttk.Button(frm, text="Search", command=self.get_match_file).grid(column=1, row=3, padx=0, pady=10)
		self.import_match_fields = tk.IntVar()
		ttk.Checkbutton(frm, text="Use other match field", name="chk_use_match", variable=self.import_match_fields) \
			.grid(column=0, row=4, padx=10, pady=5)

		ttk.Button(frm, text="Process", command=self.process).grid(column=0, row=5, padx=0, pady=10)

		ttk.Button(frm, text="Quit", command=master.destroy).grid(column=0, row=6, padx=0, pady=10)

		frm.pack()

	def get_main_file(self):
		frm = self.master.children["main_frame"]

		filename = browse_files_csv()
		frm.children["txt_filename"].delete(0, tk.END)
		frm.children["txt_filename"].insert(0, filename)

	def get_match_file(self):
		frm = self.master.children["main_frame"]

		filename = browse_files_csv()
		frm.children["txt_match"].delete(0, tk.END)
		frm.children["txt_match"].insert(0, filename)

	def process(self):
		frm = self.master.children["main_frame"]

		data = controller_get_sorted_data()

		filename = frm.children["txt_filename"].get()

		new_controller_process_cards_from_file(filename=filename, data=data)
	# match = frm.children["txt_match"].get()


def browse_files_csv():
	filename = filedialog.askopenfilename(initialdir=os.getcwd(),
	                                      title="Select a File",
	                                      filetypes=(("Comma Separated Values", "*.csv"), ("All Files", "*.*")))
	# filename = filedialog.askopenfilename(initialdir=os.getcwd(),
	#                                       title="Select a File",
	#                                       filetypes=("Comma Separated Values", "*.csv"))
	return filename


if __name__ == '__main__':
	print("Magic Processor - GUI")
	root = tk.Tk()
	myapp = App(root)
	myapp.master.title("Magic Processor")
	myapp.master.maxsize(1200, 350)
	myapp.master.minsize(350, 350)
	myapp.mainloop()
