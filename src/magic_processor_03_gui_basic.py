import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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

		ttk.Button(frm, text="Search", command=self.get_main_file).grid(column=0, row=1, padx=0, pady=10)
		ttk.Label(frm, name="btn_search_filename", text="Filename").grid(column=1, row=0, padx=10, pady=5)
		ttk.Entry(frm, name="txt_search_filename", width=48).grid(column=1, columnspan=2, row=1, padx=10, pady=5)
		ttk.Button(frm, name="btn_search_focus", text="->", command=self.focus_main). \
			grid(column=4, row=1, padx=0, pady=10)

		self.import_match_fields = tk.IntVar()
		ttk.Checkbutton(frm, text="Use match field", name="chk_use_match", variable=self.import_match_fields,
		                command=self.toggle_match_fields).grid(column=0, row=2, padx=10, pady=5)

		ttk.Label(frm, text="Match fields").grid(column=1, row=2, padx=10, pady=5)
		ttk.Button(frm, name="btn_match_filename", state="disabled", text="Search", command=self.get_match_file) \
			.grid(column=0, row=3, padx=0, pady=10)
		ttk.Entry(frm, name="txt_match_filename", state="disabled", width=48). \
			grid(column=1, columnspan=2, row=3, padx=10, pady=5)
		ttk.Button(frm, name="btn_match_focus", state="disabled", text="->", command=self.focus_match). \
			grid(column=4, row=3, padx=0, pady=10)

		ttk.Button(frm, text="Process", command=self.process).grid(column=0, row=5, padx=0, pady=10)

		ttk.Button(frm, text="Quit", command=master.destroy).grid(column=0, row=6, padx=0, pady=10)

		frm.pack()

	def get_main_file(self):
		# frm = self.master.children["main_frame"]

		filename = browse_files_csv()
		entry = self.master.children["main_frame"].children["txt_search_filename"]
		entry.delete(0, tk.END)
		entry.insert(0, filename)
		entry.xview_scroll(10, "page")
		entry.focus_set()

	# view = entry.xview()
	# print(view)
	# entry.mark_set("insert", "end")

	def focus_main(self):
		entry = self.master.children["main_frame"].children["txt_search_filename"]
		entry.xview_scroll(10, "page")
		entry.focus_set()

	def get_match_file(self):
		frm = self.master.children["main_frame"]

		filename = browse_files_csv()
		frm.children["txt_match_filename"].delete(0, tk.END)
		frm.children["txt_match_filename"].insert(0, filename)
		frm.children["txt_match_filename"].focus_set()

	def focus_match(self):
		entry = self.master.children["main_frame"].children["txt_match_filename"]
		entry.xview_scroll(10, "page")
		entry.focus_set()

	def toggle_match_fields(self):
		frm = self.master.children["main_frame"]
		# print(self.import_match_fields)
		if self.import_match_fields.get() == 0:
			frm.children["txt_match_filename"].delete(0, tk.END)
			frm.children["btn_match_filename"].config(state="disabled")
			frm.children["txt_match_filename"].config(state="disabled")
			frm.children["btn_match_focus"].config(state="disabled")
			print("Disabling match fields")
		else:
			print("Enabling match fields")
			frm.children["btn_match_filename"].config(state="normal")
			frm.children["txt_match_filename"].config(state="normal")
			frm.children["btn_match_focus"].config(state="normal")

	# frm.children["txt_match"].mark_set("insert", "end")

	def process(self):

		frm = self.master.children["main_frame"]

		filename = frm.children["txt_search_filename"].get()

		if len(filename) == 0:
			messagebox.showerror("Error", "No file entered!")
			return False

		do_continue = messagebox.askokcancel(title="Confirm",
		                                     message="Process files?")

		if not do_continue:
			return False

		data = controller_get_sorted_data()

		filename = frm.children["txt_filename"].get()

		new_controller_process_cards_from_file(filename=filename, data=data)

# match = frm.children["txt_match"].get()


def browse_files_csv():
	filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a File",
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
