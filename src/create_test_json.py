from magic_grinder_03 import NewCard
from import_scryfall_bulk_data import controller_get_sorted_data
from shared_methods_io import read_csv, write_data_json


def create_test_json(all_cards, data):
	all_scryfall_cards = []
	all_unique_scryfall_ids = set()
	for card in all_cards:
		new_card = NewCard(card)
		if new_card.try_match_self(data):
			print(new_card.name)
			if new_card.scryfall_card["id"] not in all_unique_scryfall_ids:
				all_scryfall_cards.append(new_card.scryfall_card)
				all_unique_scryfall_ids.add(new_card.scryfall_card["id"])
		else:
			print("Failed to match card!")

	return all_scryfall_cards


def controller_create_test_json(filename="audit_csv.csv"):
	data = controller_get_sorted_data()
	all_cards = read_csv(filename, True, True)

	all_scryfall_cards = create_test_json(all_cards, data)
	write_data_json(all_scryfall_cards)


if __name__ == '__main__':
	print("Creating JSON of all cards in collection.")
	controller_create_test_json()
