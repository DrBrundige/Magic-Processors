import csv
import json

from datetime import datetime, timedelta
from unidecode import unidecode
import requests


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


def call_scryfall_creature_types():
	r = requests.get('https://api.scryfall.com/catalog/creature-types')

	if r.status_code == 200:
		data = r.json()
		# print(data)
		print(data['object'])
		print(data['data'])
		return data['data']
	else:
		print('Request failed, error code: ' + str(r.status_code) + ' | ' + r.reason)
		return False


if __name__ == '__main__':
	print("Brundige's Cool Stuff")
# print(get_datetime_rounded())
# print(get_yesterday())
# print(get_epoch())
# print(count_words('I met a traveller from an antique land, who said,\n"Two vast and trunkless legs of stone...'))
