import cool_stuff
from datetime import datetime
from magic_grinder_get_card_features import *


def sort_cards_by_set(data):
	all_sorted_cards = {}
	for card in data:
		this_set = card['set']
		if this_set not in all_sorted_cards:
			all_sorted_cards[this_set] = []

		all_sorted_cards[this_set].append(card)

	return all_sorted_cards


if __name__ == '__main__':
	print("Testing card sort methods")

	# Import each printing of each card
	data = import_scryfall("default-cards-20220919210802.json")
	print("Imported cards!")
	start_time = datetime.now().timestamp()
	data = sort_cards_by_set(data)
	print("Sorted cards!")
	print(datetime.now().timestamp() - start_time)

