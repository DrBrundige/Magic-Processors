import csv
import json

from datetime import datetime, timedelta
from unidecode import unidecode


# Gets the current time with the time and second floored to zero
def get_datetime_rounded():
	time = datetime.now()
	zero = timedelta(microseconds=time.microsecond, seconds=time.second)
	return time - zero


def get_yesterday():
	time = get_datetime_rounded()
	yesterday = timedelta(hours=24)
	return time - yesterday


def get_epoch():
	return get_datetime_rounded().timestamp()


# Writes a list of dictionaries to a csv
def write_data(data, filename="out"):
	# assert that data is a list of dictionaries
	# assert that data has rows
	filename = "csvs\\" + filename + datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"

	try:
		assert isinstance(data, list), "Parameter data must be a list"
		assert len(data) > 0, "Parameter data has no rows!"

		with open(filename, 'w', newline='') as csvfile:
			print("Preparing to write")
			writer = csv.writer(csvfile, delimiter=',')

			# writes headers of first row to top of file
			headers = []
			for key, value in data[0].items():
				headers.append(key)
			writer.writerow(headers)

			# For each row in data, writes values to file
			for row in data:
				values = []
				for key, value in row.items():
					if isinstance(value, str):
						values.append(unidecode(value))
					else:
						values.append(value)
				writer.writerow(values)
	except Exception as e:
		print("Errant operation writing data!")
		print(e)
		return False
	else:
		print(f"Success! Data written to file {filename}")
		return True


# Writes a library of variables to a csv
def write_data_dictionary(data, filename="out"):
	filename = "csvs\\" + filename + datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"

	try:
		assert isinstance(data, dict), "Parameter data must be a dictionary!"
		assert len(data) > 0, "Parameter data has no rows!"

		with open(filename, 'w', newline='') as csvfile:
			print("Preparing to write")
			writer = csv.writer(csvfile, delimiter=',')

			# For each row in data, writes values to file
			for key, value in data.items():
				writer.writerow([key, value])

	except Exception as e:
		print("Errant operation writing data!")
		print(e)
		return False
	else:
		print(f"Success! Data written to file {filename}")
		return True


# Writes a list to a csv
def write_data_list(data, filename="out"):
	filename = "csvs\\" + filename + datetime.now().strftime("%Y%m%d-%H%M%S") + ".csv"

	try:
		assert isinstance(data, list), "Parameter data must be a list"
		assert len(data) > 0, "Parameter data has no rows!"

		with open(filename, 'w', newline='') as csvfile:
			print("Preparing to write")
			writer = csv.writer(csvfile, delimiter=',')

			# For each row in data, writes values to file
			for row in data:
				if isinstance(row, list):
					writer.writerow(row)
				else:
					writer.writerow([row])
	except Exception as e:
		print("Errant operation writing data!")
		print(e)
		return False
	else:
		print(f"Success! Data written to file {filename}")
		return True


# Reads from a csv file returning as a list of dictionaries
def read_csv(name="record.csv"):
	with open(name, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		headers = reader.__next__()
		data = []
		for row in reader:
			new_row = {}
			i = 0
			for header in headers:
				new_row[header] = row[i]
				i += 1
			data.append(new_row)

	print("File closed")
	return data


# Reads from Column A of a given CSV file returning a list of strings
def read_csv_list(name="all_fields.csv"):
	with open(name, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		data = []
		for row in reader:
			data.append(row[0])

	print("File closed")
	return data


# Imports JSON file with the given name. Returns a list of dictionaries
def read_json(path):
	with open(path, encoding='utf-8') as f:
		data = json.load(f)
		f.close()
		return data


# For a given list and number of characters, returns every unique set
def sets(chars, length, to_print=False, pointer=0, combo=[], all_combos=[]):
	if length > 0:
		for p in range(pointer, len(chars)):
			new_combo = combo.copy()
			new_combo.append(chars[p])
			all_combos = sets(chars, length - 1, to_print, p + 1, new_combo, all_combos)
	else:
		if to_print:
			print(f"Appending combo: {combo}")
		all_combos.append(combo)
	return all_combos


def combos(chars, length):
	all_combos = r_combos(chars, length, [], [])
	print(f"Found {len(all_combos)} combos!")
	return all_combos


def r_combos(chars, remaining, this_combo, all_combos):
	if remaining <= 0:
		add_combo = this_combo.copy()
		all_combos.append(add_combo)
		return all_combos
	else:
		for char in chars:
			this_combo.append(char)
			success = r_combos(chars, remaining - 1, this_combo, all_combos)
			this_combo.pop()
			if not success:
				return False
	return all_combos


# For a given word, returns that word in upper case with all non-letter characters removed
def clean_word(word):
	cleaned = ""
	for char in word.upper():
		if 65 <= ord(char) <= 90:
			cleaned += char
	return cleaned


# For a given string, returns that string with all non-digit characters removed
def clean_word_digits(word):
	cleaned = ""
	for char in word:
		if 48 <= ord(char) <= 57:
			cleaned += char
	return cleaned


def count_words(string):
	num_words = 0
	in_word = False

	for char in string:
		# print(char)
		if in_word:
			if char.isspace():
				in_word = False
		elif not char.isspace():
			in_word = True
			num_words += 1

	return num_words


if __name__ == '__main__':
	print("Brundige's Cool Stuff")
	# print(get_datetime_rounded())
	# print(get_yesterday())
	# print(get_epoch())
	# print(count_words('I met a traveller from an antique land, who said,\n"Two vast and trunkless legs of stone...'))
