from magic_processor_03 import NewCard
from import_scryfall_bulk_data import controller_get_sorted_data
from common_methods_io import read_csv, write_data_json


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

	return all_scryfall_cards


# Reads card information for a given filename, retrieves the latest bulk data file,
#     processes that card information, and outputs
def controller_create_test_json(filename="audit_csv.csv"):
	data = controller_get_sorted_data()
	all_cards = read_csv(filename, True, True)

	all_scryfall_cards = create_test_json(all_cards, data)
	write_data_json(all_scryfall_cards, filename="test-cards", destination="downloads")


if __name__ == '__main__':
	print("Creating JSON of all cards in collection.")
	controller_create_test_json()
