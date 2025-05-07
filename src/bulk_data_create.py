from magic_processor_03 import NewCard
from bulk_data_import import controller_get_sorted_data, controller_get_original_printings
from common_methods_io import read_csv, write_data_json
from common_methods_requests import get_set_search_uri_from_set_code, call_scryfall_03, get_download_from_uri
from datetime import datetime
import os


# Creates a JSON file similar to the bulk downloads file but orders of magnitude smaller
# The file contains the scryfall card for each card in the audit sheet
# This section matches each card in the given file and returns the scryfall card object in a list
def create_test_json(all_cards, data):
	all_scryfall_cards = []
	all_unique_scryfall_ids = set()
	for card in all_cards:
		new_card = NewCard(card)
		if new_card.try_match_self(data):
			if new_card.scryfall_card["id"] not in all_unique_scryfall_ids:
				print(new_card.name)
				all_scryfall_cards.append(new_card.scryfall_card)
				all_unique_scryfall_ids.add(new_card.scryfall_card["id"])
		else:
			print("Failed to match card!")

	write_data_json(all_scryfall_cards, filename="test-cards", destination="downloads")

	return True


def create_test_json_from_api(request_url, filename="test-cards-api"):
	output_rows = []
	do_get_json(request_url, output_rows)

	write_data_json(output_rows, filename=filename, destination="downloads")


def create_test_json_from_format(data, format="vintage"):
	print(f"Processing cards in format: {format}")
	all_scryfall_cards = []

	for scryfall_card in data:
		if "legalities" in scryfall_card and scryfall_card["legalities"][format] != "not_legal":
			all_scryfall_cards.append(scryfall_card)

	print(f"Identified {len(all_scryfall_cards)} cards")
	write_data_json(all_scryfall_cards, filename=f"test-cards-{format}", destination="downloads")


def do_get_json(request_url, output_rows):
	try:
		payload = call_scryfall_03(request_url=request_url)
		for card_object in payload['data']:
			output_rows.append(card_object)

		if payload["has_more"]:
			return do_get_json(payload["next_page"], output_rows)
		else:
			return output_rows
	except Exception as E:
		print(f"Errant operation getting test data from API!")
		print(E)
		return False


def create_set_data_json():
	data = call_scryfall_03("https://api.scryfall.com/sets/")
	write_data_json(data=data['data'], filename="all-sets", destination="downloads")


def get_all_set_names_with_type(set_types):
	data = call_scryfall_03("https://api.scryfall.com/sets/")
	today = datetime.today().strftime("%Y-%m-%d")
	all_set_names = []
	for set in data["data"]:
		if set["set_type"] in set_types and not set["digital"] and set["released_at"] <= today:
			all_set_names.append(set["code"].upper())

	return all_set_names


def get_all_set_names():
	data = call_scryfall_03("https://api.scryfall.com/sets/")
	all_set_names = []
	for set in data["data"]:
		all_set_names.append(set["code"].upper())

	return all_set_names


def create_set_names_json(set_types=None):
	if set_types is None:
		all_sets = get_all_set_names()
	else:
		all_sets = get_all_set_names_with_type(set_types)
	# set_json = {"sets": all_sets}
	write_data_json(data=all_sets, filename="all-sets-names", destination="downloads")

	return True


def create_set_names_json_major_sets():
	set_types = ["expansion", "core", "masters", "draft_innovation"]
	return create_set_names_json(set_types=set_types)


def download_latest_json_files(bulk_names=None):
	if bulk_names is None:
		bulk_names = ["oracle_cards", "unique_artwork", "default_cards"]
	payload = call_scryfall_03(endpoint="bulk-data")

	valid_names = check_existing_json_files(payload, bulk_names)

	if len(valid_names) == 0:
		print("No valid names!")
		return False

	for bulk in payload["data"]:
		if (bulk["type"]) in valid_names:
			print(f"Attempting to download bulk file with type: {bulk['type']}")
			filename = bulk["download_uri"].split("/")[-1]
			get_download_from_uri(uri=bulk["download_uri"], file_name=f"downloads/{filename}")

	return True


# Using a process similar to bulk_data_import.get_latest_json,
# checks to see if bulk files are already in downloads folder
def check_existing_json_files(payload, bulk_names):
	valid_names = []

	# Loops through each item in the data payload. We will look for items with the same type field as the bulk names
	for bulk_item in payload["data"]:
		if (bulk_item["type"]) in bulk_names:
			uri_endpoint = bulk_item["download_uri"].split("/").pop()

			all_files = os.listdir("downloads")
			all_files = [f for f in all_files if os.path.isfile("downloads" + '/' + f)]

			# for file in all_files:
			if uri_endpoint in all_files:
				print(f"Bulk data file {bulk_item['type']} already downloaded!")
			else:
				valid_names.append(bulk_item["type"])

	return valid_names


# Reads card information for a given filename, retrieves the latest bulk data file,
#     processes that card information, and outputs,
#     This creates a JSON file that contains the exact cards from the named file,
#     that can later be imported much faster for testing purposes
def controller_create_test_json(filename="audit_csv.csv"):
	data = controller_get_sorted_data()
	all_cards = read_csv(filename, True, True)

	create_test_json(all_cards, data)


# write_data_json(all_scryfall_cards, filename="test-cards", destination="downloads")


def controller_create_test_json_from_set(set='woe'):
	set_url = get_set_search_uri_from_set_code(set)
	create_test_json_from_api(set_url, filename=f"test-cards-{set}")


# Do not use this. Use new_controller_process_all_cards_in_data_file to create a CSV with all cards in it,
#   manipulate as needed, then create a test JSON with controller_create_test_json instead.
def controller_create_test_json_from_format_cards(format="vintage"):
	print(f"Creating JSON of cards in format: {format}")
	# request_url = f"https://api.scryfall.com/cards/search?q=f%3A{format}&unique=cards&order=name"
	# create_test_json_from_api(request_url, filename=format)
	data = controller_get_original_printings()
	create_test_json_from_format(data, format)


if __name__ == '__main__':
	print("Creating new JSON download files.")
	# controller_create_test_json_from_set("OTJ")
	# controller_create_test_json(filename="all_eternal_cards.csv")
	# controller_create_test_json_from_format_cards(format="standard")
	# create_test_json_from_api("https://api.scryfall.com/cards/search?q=year%3A2023","test-cards-2023")
	# download_latest_json_files()
	# create_sets_json()
	create_set_names_json_major_sets()
	print("Downloaded latest bulk data files!")

# controller_create_test_json()
