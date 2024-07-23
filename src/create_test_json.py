from magic_processor_03 import NewCard
from import_scryfall_bulk_data import controller_get_sorted_data
from common_methods_io import read_csv, write_data_json
from common_methods_call_scryfall import get_set_search_uri_from_set_code, call_scryfall_03, get_download_from_uri


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


def download_latest_json_files(bulk_items=None):
	if bulk_items is None:
		bulk_items = ["oracle_cards", "unique_artwork", "default_cards"]
	payload = call_scryfall_03(endpoint="bulk-data")
	for bulk in payload["data"]:
		if (bulk["type"]) in bulk_items:
			# print(bulk["type"])
			filename = bulk["download_uri"].split("/")[-1]
			# print(filename)
			get_download_from_uri(uri=bulk["download_uri"], file_name=f"downloads/{filename}")



# Reads card information for a given filename, retrieves the latest bulk data file,
#     processes that card information, and outputs
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
	request_url = f"https://api.scryfall.com/cards/search?q=f%3A{format}&unique=cards&order=name"
	create_test_json_from_api(request_url, filename=format)


if __name__ == '__main__':
	print("Creating JSON of all cards in collection.")
	# controller_create_test_json_from_set("OTJ")
	# controller_create_test_json(filename="all_eternal_cards.csv")
	# controller_create_test_json_from_format_cards()
	download_latest_json_files()
