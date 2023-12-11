import csv
import json

from datetime import datetime, timedelta
from unidecode import unidecode


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
					for i in range(len(row)):
						row[i] = unidecode(row[i])

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


# Writes a dictionary or perhaps list of dictionaries to a json file
# Outputs filename in a slightly different format
def write_data_json(data, filename="out", destination="bin"):
	filename = f"{destination}\\{filename}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
	try:
		assert isinstance(data, list), "Parameter data must be a list"
		assert len(data) > 0, "Parameter data has no rows!"

		data_string = json.dumps(data, indent=2)

		f = open(filename, "w")
		f.write(data_string)
		f.close()

	except Exception as E:
		print("Errant operation writing JSON!")
		print(E)
		return False
	else:
		print(f"Success! Data written to file {filename}")
		return True


# Reads from a csv file returning as a list of dictionaries
# do_snake_case_names - if True, puts header names into lower case with underscores
# do_standardize_header_names - runs header names through a dictionary
#   replacing header names with a set list that the code will expect.
#   Note: only runs if do_snake_case_names is also set to True.
def read_csv(name="record.csv", do_snake_case_names=False, do_standardize_header_names=False):
	with open(name, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		headers = reader.__next__()

		if do_snake_case_names:
			lower_headers = []
			for header in headers:
				lower_headers.append(snake_case_parameter(header))
			headers = lower_headers

		if do_snake_case_names and do_standardize_header_names:
			standardize_header_names(headers)

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


# Reads from a csv file returning the first row as a list
def read_csv_get_headers(name="record.csv", do_snake_case_names=False, do_standardize_header_names=False):
	print("Accessing file to return header row")
	with open(name, newline='') as csvfile:
		reader = csv.reader(csvfile, delimiter=',', quotechar='"')
		headers = reader.__next__()

		if do_snake_case_names:
			lower_headers = []
			for header in headers:
				lower_headers.append(snake_case_parameter(header))
			headers = lower_headers

		if do_snake_case_names and do_standardize_header_names:
			standardize_header_names(headers)

	print("File closed")
	return headers


# Imports JSON file with the given name. Returns a list of dictionaries
def read_json(path):
	with open(path, encoding='utf-8') as f:
		data = json.load(f)
		f.close()
		return data


# Imports TXT file with the given name. Returns a list of strings
def read_txt(path):
	with open(path, encoding='utf-8') as f:
		text = []
		for line in f:
			text.append(unidecode(line.strip()))
		f.close()
		# print(text)
		return text


# No I/O is happening here, but these methods are necessary to support read_csv
def snake_case_parameter(name):
	name = name.lower()
	name = name.strip()
	name = name.replace(' ', '_')
	name = name.replace('.', '')
	return name


# Modifies a list of headers. Returns True or False for success
# Accepts a list of strings, a string path
def standardize_header_names(headers, replacement_path="standardized_headers.json"):
	# Read from a JSON of headers
	replacements = read_json(f"bin/{replacement_path}")

	for replacement in replacements.keys():
		if replacement in headers:
			i = headers.index(replacement)
			headers[i] = replacements[replacement]

	# For object in read JSON, try to replace the name of each header
	return True


if __name__ == '__main__':
	print("Brundige's Cool Stuff")
	read_txt("bin/decklist.txt")
# read_csv("audit_csv.csv", True, True)
