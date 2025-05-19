import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from bulk_data_import import controller_get_sorted_data
from magic_processor_03 import get_cards_from_api, get_cards_from_file, output_bound_cards, get_all_cards_from_data_file
from bulk_data_import import get_latest_json
from bulk_data_create import do_get_json, download_latest_json_files, check_existing_json_files, \
	create_set_names_json_major_sets
from common_methods_io import read_json, read_csv_get_headers, write_data_list
from common_methods_requests import get_set_search_uri_from_set_code, call_scryfall_03


class App(ttk.Frame):
	chk_use_card_source = 0
	chk_use_match_fields = 0
	rad_data_source = ""

	chk_do_sort = 0

	data = []

	def __init__(self, master):
		super().__init__(master)
		self.pack()

		# window = tk.Tk()
		frm = ttk.Frame(master, padding=20, name="main_frame")

		# Card source

		(ttk.Label(frm, name="lbl_source", text="Card source", font=("vollkorn", 14, "bold"), justify="left")
		 .grid(column=0, row=0, padx=10, pady=5, sticky="w"))

		self.chk_use_card_source = tk.IntVar()
		ttk.Checkbutton(frm, text="Use card source", name="chk_use_source", variable=self.chk_use_card_source,
		                command=self.update_disabled_fields).grid(column=0, row=1, padx=10, pady=5)
		self.chk_use_card_source.set(True)

		(ttk.Button(frm, name="btn_source", text="Search", command=self.get_file_source).
		 grid(column=0, row=2, padx=5, pady=10))
		(ttk.Entry(frm, name="txt_source", width=48).
		 grid(column=1, columnspan=2, row=2, padx=5, pady=5))
		ttk.Button(frm, name="btn_source_focus", text="->", command=self.focus_source). \
			grid(column=4, row=2, padx=5, pady=10)
		ttk.Button(frm, name="btn_source_clear", text="Clear", command=self.clear_source). \
			grid(column=5, row=2, padx=5, pady=10)

		ttk.Label(frm, name="lbl_source_count", text="Count field").grid(column=0, row=3)
		ttk.Entry(frm, name="txt_source_count").grid(column=1, row=3, padx=5, pady=5, sticky="w")

		# Match fields

		(ttk.Label(frm, name="lbl_match", text="Match fields", font=("vollkorn", 14, "bold"), justify="left")
		 .grid(column=0, row=10, padx=10, pady=5, sticky="w"))

		self.chk_use_match_fields = tk.IntVar()
		ttk.Checkbutton(frm, text="Use match field", name="chk_use_match", variable=self.chk_use_match_fields,
		                command=self.update_disabled_fields).grid(column=0, row=11, padx=10, pady=5)

		ttk.Button(frm, name="btn_match", text="Search", command=self.get_file_match).grid(column=0, row=12, padx=5,
		                                                                                   pady=10)
		ttk.Entry(frm, name="txt_match", width=48).grid(column=1, columnspan=2, row=12, padx=5, pady=5)
		ttk.Button(frm, name="btn_match_focus", text="->", command=self.focus_match). \
			grid(column=4, row=12, padx=5, pady=10)
		ttk.Button(frm, name="btn_match_clear", text="Clear", command=self.clear_match). \
			grid(column=5, row=12, padx=5, pady=10)

		# Data source

		(ttk.Label(frm, name="lbl_data", text="Data source", font=("vollkorn", 14, "bold"), justify="left")
		 .grid(column=0, row=20, padx=10, pady=5, sticky="w"))

		self.rad_data_source = tk.StringVar()
		ttk.Radiobutton(frm, text="Use data file", name="rad_data_file", variable=self.rad_data_source, value="file",
		                command=self.update_disabled_fields).grid(column=0, row=21, padx=10, pady=5)
		ttk.Radiobutton(frm, text="Use set (API)", name="rad_set", variable=self.rad_data_source, value="set",
		                command=self.update_disabled_fields).grid(column=4, row=21, padx=10, pady=5)
		self.rad_data_source.set("file")

		(ttk.Button(frm, name="btn_data_file", text="Search", command=self.get_data_file).
		 grid(column=0, row=22, padx=5, pady=10))
		ttk.Entry(frm, name="txt_data_file", width=48).grid(column=1, columnspan=2, row=22, padx=5, pady=5, sticky="w")
		ttk.Combobox(frm, name="ddl_data_set").grid(column=4, columnspan=2, row=22, padx=0, pady=5)

		# Confirm input

		ttk.Separator(frm, orient="horizontal").grid(column=0, columnspan=6, row=30, sticky="we", padx=5)

		self.chk_do_sort = tk.IntVar()
		(ttk.Checkbutton(frm, text="Sort output", name="chk_do_sort", variable=self.chk_do_sort)
		 .grid(column=0, row=31, padx=10, pady=5))

		(ttk.Button(frm, name="btn_load_data", text="Load data", command=self.load_data).
		 grid(column=0, row=32, padx=5, pady=10))
		(ttk.Button(frm, name="btn_clear_data", text="Clear data", command=self.clear_data_source).
		 grid(column=1, row=32, sticky="w", padx=5, pady=10))
		(ttk.Button(frm, name="btn_update_data", text="Update data sources", command=self.update_data_sources).
		 grid(column=2, row=32, padx=5, pady=10))

		(ttk.Button(frm, name="btn_process", text="Process", command=self.process_data).
		 grid(column=0, row=33, padx=5, pady=10))

		ttk.Button(frm, text="Quit", command=master.destroy).grid(column=0, row=100, padx=0, pady=10)

		frm.pack()

		self.update_disabled_fields()
		self.reload_set_names()
		self.reload_latest_bulk_file()

	def update_disabled_fields(self):
		frm = self.master.children["main_frame"]

		if self.chk_use_card_source.get():
			state_card_source = "normal"
		else:
			state_card_source = "disabled"

		if self.chk_use_match_fields.get():
			state_match_fields = "normal"
		else:
			state_match_fields = "disabled"

		# print(self.rad_data_source.get())
		if self.rad_data_source.get() == "file":
			state_data_file = "normal"
			state_data_set = "disabled"
		else:
			state_data_file = "disabled"
			state_data_set = "normal"

		# I'm sure there's a way to make this smarter. Put all these fields in their own container or something. Eh.

		frm.children["btn_source"].config(state=state_card_source)
		frm.children["txt_source"].config(state=state_card_source)
		frm.children["btn_source_focus"].config(state=state_card_source)
		frm.children["btn_source_clear"].config(state=state_card_source)
		frm.children["txt_source_count"].config(state=state_card_source)

		frm.children["btn_match"].config(state=state_match_fields)
		frm.children["txt_match"].config(state=state_match_fields)
		frm.children["btn_match_focus"].config(state=state_match_fields)
		frm.children["btn_match_clear"].config(state=state_match_fields)

		frm.children["btn_data_file"].config(state=state_data_file)
		frm.children["txt_data_file"].config(state=state_data_file)
		frm.children["ddl_data_set"].config(state=state_data_set)

	def reload_latest_bulk_file(self):
		frm = self.master.children["main_frame"]
		latest_file_name = get_latest_json("default-cards")
		if len(latest_file_name) > 0:
			frm.children["txt_data_file"].insert(tk.END, latest_file_name)

	def reload_set_names(self):
		frm = self.master.children["main_frame"]
		latest_file_name = get_latest_json("all-sets-names")
		if len(latest_file_name) > 0:
			all_sets_names = read_json("downloads/" + latest_file_name)

			frm.children["ddl_data_set"].config(values=all_sets_names)
			frm.children["ddl_data_set"].set(all_sets_names[0])

	# Search button (file)
	def get_file_source(self):
		filename = browse_files_csv()

		if len(filename) > 0:
			entry = self.master.children["main_frame"].children["txt_source"]
			entry.delete(0, tk.END)
			entry.insert(0, filename)

	# -> button (file)
	def focus_source(self):
		entry = self.master.children["main_frame"].children["txt_source"]
		entry.xview_scroll(10, "page")
		entry.focus_set()

	# Clear button (file)
	def clear_source(self):
		self.master.children["main_frame"].children["txt_source"].delete(0, "end")
		self.master.children["main_frame"].children["txt_source_count"].delete(0, "end")

	# Search button (match)
	def get_file_match(self):
		filename = browse_files_csv()

		if len(filename) > 0:
			entry = self.master.children["main_frame"].children["txt_match"]
			entry.delete(0, tk.END)
			entry.insert(0, filename)

	# -> button (match)
	def focus_match(self):
		entry = self.master.children["main_frame"].children["txt_match"]
		entry.xview_scroll(10, "page")
		entry.focus_set()

	# Clear button (match)
	def clear_match(self):
		self.master.children["main_frame"].children["txt_match"].delete(0, "end")

	# Search button (data source)
	def get_data_file(self):
		filename = filedialog.askopenfilename(initialdir=f"{os.getcwd()}\downloads", title="Select a File",
		                                      filetypes=(("JSON", "*.json"), ("All Files", "*.*")))

		if len(filename) > 0:
			entry = self.master.children["main_frame"].children["txt_data_file"]
			entry.delete(0, tk.END)
			entry.insert(0, filename)

	# Load data button
	def load_data(self):
		if self.rad_data_source.get() == "file":
			return self.load_data_file()
		else:
			return self.load_data_set()

	# Called by load_data()
	def load_data_file(self):
		data_file_path = self.master.children["main_frame"].children["txt_data_file"].get()

		do_continue = data_file_path.endswith(".json")

		if not do_continue:
			return self.throw_error(title="Error loading data", message=f"Input file is not JSON: {data_file_path}")

		if os.path.isfile("downloads" + '/' + data_file_path):
			do_continue = True
			data_file_path = "downloads" + '/' + data_file_path
		elif os.path.isfile(data_file_path):
			do_continue = True
		else:
			do_continue = False

		if not do_continue:
			return self.throw_error(title="Error loading data", message=f"No file found for: {data_file_path}")

		do_continue = messagebox.askokcancel(title="Load data from file",
		                                     message=f"Load data from file? {data_file_path}")

		if not do_continue:
			print("User cancelled")
			return False

		print("Loading data file")

		print("Importing Scryfall test card data at " + data_file_path)
		data = read_json(data_file_path)
		print(f"Success! Imported {len(data)} cards!")

		if len(data) > 0:
			self.data = data
			messagebox.showinfo(title="Data file loaded", message=f"Success! Imported {len(data)} cards!")
		else:
			return self.throw_error(title="Error loading data", message=f"No cards imported for: {data_file_path}")

		return True

	# Called by load_data()
	def load_data_set(self):
		do_continue = messagebox.askokcancel(title="Load data from API", message="Load set data from API?")

		if not do_continue:
			print("User cancelled")
			return False

		data_set_code = self.master.children["main_frame"].children["ddl_data_set"].get()
		print(data_set_code)

		search_uri = get_set_search_uri_from_set_code(data_set_code)

		if len(search_uri) == 0:
			self.throw_error(title="Error loading set", message=f"Could not find set: {data_set_code}")

		print(search_uri)
		# Calls the bulk data create method instead of the magic_processor_03 method,
		# which returns the rows already bound. We need this data raw so the processor can match it later.
		data = do_get_json(search_uri, [])
		# data = get_cards_from_api(search_uri)
		# print(len(data))

		if len(data) > 0:
			self.data = data
			messagebox.showinfo(title="Set data loaded", message=f"Success! Imported {len(data)} cards!")
		else:
			return self.throw_error(title="Error loading data", message=f"No cards found for: {data_set_code}")

		return True

	# Process button
	def process_data(self):
		# Checks card source is provided
		frm = self.master.children["main_frame"]

		if self.chk_use_card_source.get() and len(frm.children["txt_source"].get()) == 0:
			frm.children["txt_source"].xview_scroll(10, "page")
			frm.children["txt_source"].focus_set()
			return self.throw_error(title="Cannot process data", message="No card source provided!")

		if self.chk_use_match_fields.get() and len(frm.children["txt_match"].get()) == 0:
			frm.children["txt_match"].xview_scroll(10, "page")
			frm.children["txt_match"].focus_set()
			return self.throw_error(title="Cannot process data", message="No match fields provided!")

		if not self.chk_use_card_source.get() and not self.chk_use_match_fields.get():
			return self.throw_error(title="Cannot process data",
			                        message="Either card source or match fields must be provided!")

		# Verifies data is loaded
		if len(self.data) == 0:
			# If data is not loaded, asks user to load data
			do_continue = messagebox.askokcancel(title="Load data?", message=f"No data loaded. Load data now?")
			if do_continue:
				# Attempts to load data. If unsuccessful, returns false
				do_continue = self.load_data()
				if not do_continue:
					return False
			else:
				return messagebox.showerror(title="Cannot process data", message="No data loaded!")

		print(len(self.data))

		# Checks if use card source is checked. This determines the sequence used
		if self.chk_use_card_source.get():
			count = frm.children["txt_source_count"].get()
			card_source_filename = frm.children["txt_source"].get()
			if self.chk_use_match_fields.get():
				match_fields_filename = frm.children["txt_match"].get()
				return self.process_cards_with_source(card_source_filename=card_source_filename,
				                                      match_fields_filename=match_fields_filename, count=count)
			else:
				return self.process_cards_with_source(card_source_filename=card_source_filename,
				                                      match_fields_filename=None, count=count)
		else:
			match_fields_filename = frm.children["txt_match"].get()
			return self.process_all_cards(match_fields_filename=match_fields_filename)

	# Called by process_data()
	def process_cards_with_source(self, card_source_filename, match_fields_filename=None, count=""):
		# Reads cards from source
		all_new_cards = get_cards_from_file(card_source_filename, self.data)
		# header_row = []

		# If match fields is provided, uses that file name. Otherwise, uses the card source
		if match_fields_filename is None or len(match_fields_filename) == 0:
			match_fields = read_csv_get_headers(name=card_source_filename, do_standardize_header_names=True,
			                                    do_snake_case_names=True)
			header_row = read_csv_get_headers(name=card_source_filename)
		else:
			match_fields = read_csv_get_headers(name=match_fields_filename, do_standardize_header_names=True,
			                                    do_snake_case_names=True)
			header_row = read_csv_get_headers(name=match_fields_filename)

		# Processes cards
		output_rows = output_bound_cards(all_new_cards, match_fields, count_field=count)

		if len(output_rows) == 0:
			return self.throw_error("Error processing tickets", "No rows to output! Aborting")

		output_rows.insert(0, header_row)
		if write_data_list(output_rows, "source"):
			messagebox.showinfo(title="Cards processed",
			                    message=f"Success! Data written successfully! Wrote {len(output_rows)} rows")

		return True

	# Called by process_data()
	def process_all_cards(self, match_fields_filename):
		# Reads cards from source
		all_new_cards = get_all_cards_from_data_file(self.data)

		# Gets match fields and header row
		match_fields = read_csv_get_headers(name=match_fields_filename, do_standardize_header_names=True,
		                                    do_snake_case_names=True)
		header_row = read_csv_get_headers(name=match_fields_filename)

		# Processes cards
		output_rows = output_bound_cards(all_new_cards, match_fields)

		if len(output_rows) == 0:
			return self.throw_error("Error processing tickets", "No rows to output! Aborting")

		output_rows.insert(0, header_row)
		if write_data_list(output_rows, "all_cards"):
			messagebox.showinfo(title="Cards processed",
			                    message=f"Success! Data written successfully! Wrote {len(output_rows)} rows")

		return True

	# Clear data
	def clear_data_source(self):
		if messagebox.askokcancel(title="Clear data", message="Clear data?"):
			self.data = []

	# Update data source
	def update_data_sources(self):
		if messagebox.askokcancel(title="Update data sources",
		                          message="Update data sources? This operation may take some time"):
			print("Updating data source")
			try:
				bulk_names = ["oracle_cards", "unique_artwork", "default_cards"]
				payload = call_scryfall_03(endpoint="bulk-data")
				valid_names = check_existing_json_files(payload, bulk_names)
				if len(valid_names) > 0:
					if (download_latest_json_files()):
						messagebox.showinfo(title="Success", message="Bulk data files downloaded successfully.")
					else:
						self.throw_error(title="Error downloading bulk files", message=f"Bulk download failed!")
				else:
					messagebox.showinfo(title="No data files downloaded",
					                    message="All data files already downloaded")
			except Exception as E:
				print(E)
				self.throw_error(title="Error downloading bulk files", message=f"Error downloading bulk files {E}")

			try:
				if (create_set_names_json_major_sets()):
					messagebox.showinfo(title="Success", message="Set file created successfully!")
					self.reload_set_names()
				else:
					self.throw_error(title="Error downloading bulk files", message=f"Set file creation was unsuccessful!")

			except Exception as E:
				print(E)
				self.throw_error(title="Error downloading bulk files", message=f"Error downloading set file {E}")

	def throw_error(self, title="Error processing tickets", message="Errant operation"):
		print(message)
		messagebox.showerror(title=title, message=message)
		return False


def browse_files_csv():
	filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select a File",
	                                      filetypes=(("Comma Separated Values", "*.csv"), ("All Files", "*.*")))

	return filename


# noinspection PyPackageRequirements
if __name__ == '__main__':
	print("Magic processor gui")
	root = tk.Tk()
	myapp = App(root)

	myapp.master.title("Magic Processor")

	# photo = tk.PhotoImage(file="")
	try:
		root.iconbitmap(True, "images/magic_processor_icon.ico")
	except Exception as E:
		print("Could not assign icon")
		print(E)

	root.update()  # Ensure the window is drawn
	width = root.winfo_width()
	height = root.winfo_height()

	print(f"Width {width} | Height {height}")

	# myapp.master.maxsize(width, height)
	myapp.master.minsize(width, height)
	myapp.mainloop()
