import os
import common_methods_io
from datetime import *
from common_methods_processor_03 import sort_cards_by_set_num


# Imports the latest full Scryfall download file containing each printing of each card.
def import_scryfall_full():
	# Identifies most recent bulk download file
	path = get_latest_json("default-cards")
	print("Importing full Scryfall data at " + path)
	# Parses JSON file at that location
	data = common_methods_io.read_json("downloads/" + path)
	print(f"Success! Imported {len(data)} cards!")
	return data


# Imports the latest abridged Scryfall download file containing one printing for each unique card name.
def import_scryfall_abridged():
	path = get_latest_json("oracle-cards")
	print("Importing abridged Scryfall data at " + path)
	data = common_methods_io.read_json("downloads/" + path)
	print(f"Success! Imported {len(data)} cards!")
	return data


# Imports the latest abridged Scryfall download file containing one printing for each unique card art.
def import_scryfall_art():
	path = get_latest_json("unique-artwork")
	print("Importing Scryfall unique art data at " + path)
	data = common_methods_io.read_json("downloads/" + path)
	print(f"Success! Imported {len(data)} cards!")
	return data


# Imports the latest abridged Scryfall download file containing one printing for each unique card art.
def import_scryfall(json_prefix="test-cards"):
	path = get_latest_json(json_prefix)
	print("Importing Scryfall test card data at " + path)
	data = common_methods_io.read_json("downloads/" + path)
	print(f"Success! Imported {len(data)} cards!")
	return data


# Parses all bulk download files in the downloads folder and returns the name of the most recent one as a string
def get_latest_json(json_class="oracle-cards"):
	# Identifies files in the downloads folder
	all_files = os.listdir("downloads")
	all_files = [f for f in all_files if os.path.isfile("downloads" + '/' + f)]

	# Identifies all JSON files in downloads directory
	all_jsons = []
	for file in all_files:
		if file.endswith(".json"):
			all_jsons.append(file)

	# Strips json files of the timestamps
	all_timestamps = []
	for json in all_jsons:
		if json.startswith(json_class):
			try:
				all_timestamps.append(int(json[len(json_class) + 1:-5]))
			except Exception as E:
				pass
	# print("Errant operation converting timestamp to int")
	# print(E)

	# Sorts timestamps
	if len(all_timestamps) == 0:
		print(f"Errant operation finding json for class {json_class}!"
		      f"No files with that name were found")
		return ""

	all_timestamps.sort(reverse=True)

	# Recombines the name of the most recent json file and returns
	return f"{json_class}-{all_timestamps[0]}.json"


# For a given dataset, sorts each card by set.
# Returns a dictionary
def sort_cards_by_set(data):
	all_sorted_cards = {}
	for card in data:
		this_set = card['set']
		if this_set not in all_sorted_cards:
			all_sorted_cards[this_set] = []

		all_sorted_cards[this_set].append(card)

	return all_sorted_cards


# For a given dataset, sorts each card by a given field. Defaults to name
# Returns a dictionary
def sort_cards_by_field(data, field="name"):
	all_sorted_cards = {}
	for card in data:
		this_field = card[field]
		if this_field not in all_sorted_cards:
			all_sorted_cards[this_field] = []

		all_sorted_cards[this_field].append(card)

	return all_sorted_cards


# For a given dataset, filters out any card that is a reprint,
#     returning the original printing for each card with the lowest set number
# def sort_cards_by_original_printing(data):
# 	all_original_cards = {}
# 	# Iterates through parameterized data object
#
# 	for card in data:
# 		if not card["reprint"]:
# 			card_name = card["name"]
# 			# If the card is not in the dictionary, adds it
# 			if card_name not in all_original_cards:
# 				all_original_cards[card_name] = card
# 			# If this card has a lower set number than the version currently in the dictionary, replaces it
# 			elif all_original_cards[card_name]["collector_number"] > card["collector_number"]:
# 				all_original_cards[card_name] = card
#
# 	# Flattens dictionary into a list. Returns
# 	all_cards_list = []
# 	for key in all_original_cards:
# 		all_cards_list.append(all_original_cards[key])
#
# 	return all_cards_list

# For a given dataset, filters out any card that is a reprint,
#     returning the original printing for each card with the lowest set number
def sort_cards_by_original_printing(data):
	data_sorted = sort_cards_by_field(data, "name")
	all_cards_list = []

	for card_name in data_sorted:
		sorted_card_details = sort_cards_by_set_num(data_sorted[card_name])
		sorted_card_details.sort(key=sort_set)
		sorted_card_details.sort(key=sort_release)
		all_cards_list.append(sorted_card_details[0])

	return all_cards_list


def sort_release(card):
	return card["released_at"]


def sort_set(card):
	return card["set"]


# Returns the dataset at the given path sorted by set code
def controller_get_sorted_data(path="default-cards"):
	# Import each printing of each card
	then = datetime.now().timestamp()

	path = get_latest_json(path)
	print("Importing Scryfall data at " + path)
	# Parses JSON file at that location
	data = common_methods_io.read_json("downloads/" + path)

	# Sorts all cards into a dictionary by set
	data_sorted = sort_cards_by_set(data)
	now = datetime.now().timestamp()
	print(f"Sorted cards! Imported and sorted {len(data)} cards in {now - then} seconds!")
	return data_sorted


# Returns the dataset at the given path sorted by set code
def controller_get_sorted_data_by_field(path="default-cards", field="name"):
	# Import each printing of each card
	then = datetime.now().timestamp()

	path = get_latest_json(path)
	print("Importing Scryfall data at " + path)
	# Parses JSON file at that location
	data = common_methods_io.read_json("downloads/" + path)

	# Sorts all cards into a dictionary by set
	data_sorted = sort_cards_by_field(data, field)
	now = datetime.now().timestamp()
	print(f"Sorted cards! Imported and sorted {len(data)} cards by {field} in {now - then} seconds!")
	return data_sorted


# Returns the full dataset, with any reprints filtered out such that in affect it has the same cards the abridged data
def controller_get_original_printings():
	# then = datetime.now().timestamp()
	then = datetime.now().timestamp()
	data = import_scryfall_full()
	print("Imported cards!")
	original_printings = sort_cards_by_original_printing(data)
	now = datetime.now().timestamp()
	print(
		f"Sorted cards by original printing! Imported and sorted {len(original_printings)} cards in {now - then} seconds!")
	return original_printings


def controller_get_test_data():
	print("Importing test data")
	data = common_methods_io.read_json("bin/all_khm_cards.json")
	sorted_data = sort_cards_by_set(data)

	print(f"Success! Imported and sorted {len(data)} cards!")
	return sorted_data


if __name__ == '__main__':
	print("Testing Import Scryfall methods")
	controller_get_original_printings()
