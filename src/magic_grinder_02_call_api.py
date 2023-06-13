import time

import requests
from magic_grinder_02_methods_card_processors import *
from shared_methods_io import write_data


# Don't get me wrong - my search methods work,
# but sometimes it's best to get data straight from the source.


# Attempts to contact the Scryfall API.
#   This method uses no access token, so only basic information may be retrieved.
#   Nevertheless, this includes a wide range of data
# Returns data payload as list of strings on success. Returns None on fail
# Also, not all Scryfall requests return a data object, but I'm too lazy to fix it right now
def call_scryfall(endpoint="sets/khm", return_full_data_object=False, full_url=""):
	try:
		print("Contacting Scryfall API")
		time.sleep(.1)

		if len(full_url) > 0:
			r = requests.get(full_url)
		else:
			r = requests.get(f'https://api.scryfall.com/{endpoint}')

		if r.status_code == 200:
			data = r.json()
			if "data" in data:
				print(f"Success! Returned {len(data['data'])} rows")
			else:
				print(f"Success! Returned data object!")
			# print(data)
			# print(data['object'])
			# print(data['data'])
			if return_full_data_object:
				return data
			else:
				return data['data']
		else:
			print('Request failed, error code: ' + str(r.status_code) + ' | ' + r.reason)
			return None
	except Exception as E:
		print("Error contacting Scryfall!")
		print(E)
		return None


# Calls Scryfall API and attempts to parse information
# Searches each return row for parameterized strings and returns those fields as a list of strings
# Returns data on success.
def parse_scryfall_data(endpoint, fields):
	data = call_scryfall(endpoint)
	new_rows = []
	for scryfall_object in data:
		new_row = {}
		for field in fields:
			if field in scryfall_object:
				new_row[field] = scryfall_object[field]
			else:
				new_row[field] = ""
		new_rows.append(new_row)

	return new_rows


# Controller. Calls parse_scryfall_data() to retrieve information on all sets and prints
def controller_get_set_data():
	fields = ["code", "name", "released_at"]
	set_data = parse_scryfall_data("sets", fields)
	write_data(set_data, "sets")


# Controller. Calls call_scryfall() to retrieve each creature type and returns as list of strings
def controller_get_scryfall_creature_types():
	# r = requests.get('https://api.scryfall.com/catalog/creature-types')
	return call_scryfall("catalog/creature-types")


def process_cards_from_scryfall(api_string, processor_method):
	bound_cards = []
	failed_objects = []
	do_process_scryfall_object(api_string, bound_cards, failed_objects, processor_method)

	# print(scryfall_object)
	print("Yearning 4 my bestie.")
	print(f"Bound cards: {len(bound_cards)}")
	print(f"Failed objects: {len(failed_objects)}")

	return bound_cards


def do_process_scryfall_object(api_string, bound_cards, failed_objects, processor_method):
	try:
		scryfall_object = call_scryfall(full_url=api_string, return_full_data_object=True)
		if scryfall_object is not None:
			for scryfall_card in scryfall_object['data']:
				try:
					card = {}
					# Processes bulk data object for output using the parameterized method
					if processor_method(scryfall_card, card):
						bound_cards.append(card)
					else:
						failed_objects.append(scryfall_card)

				except Exception as E:
					print(f"Errant operation parsing card {scryfall_card['name']}")
					print(E)
					failed_objects.append(scryfall_card)
		else:
			return False
	except Exception as E:
		print("Errant operation processing Scryfall object!")
		print(E)
		return False

	if scryfall_object['has_more']:
		return do_process_scryfall_object(scryfall_object["next_page"], bound_cards, failed_objects, processor_method)
	else:
		return True


def controller_get_set_sheet_from_scryfall():
	print("Processing cards from Scryfall API")
	set_data = call_scryfall(endpoint="sets/dmu", return_full_data_object=True)
	# https://api.scryfall.com/cards/search?order=name&q=c%3#Ared+pow%3#D3
	set_rows = process_cards_from_scryfall(set_data["search_uri"], get_set_sheet)
	write_data(set_rows, "set")


if __name__ == '__main__':
	print("Calling Scryfall API")
	# call_scryfall("bingus")
	# print(controller_get_scryfall_creature_types())
	controller_get_set_sheet_from_scryfall()
# controller_get_set_data()
