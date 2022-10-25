from shared_methods_io import write_data
from import_scryfall import import_scryfall_abridged, import_scryfall_art, import_scryfall_full
from sort_card_data import sort_cards_by_set

from magic_grinder_02_custom_scan_methods import *
from magic_grinder_02_scryfall_card_scanners import *


# Scans bulk data (either full or abridged) and outputs cards in a list.
#    Unlike the bulk matcher, accepts multiple matching methods
def scan_bulk_data_list(data, match_methods, processor_method):
	scanned_cards = []
	failed_cards = []

	for scryfall_card in data:
		try:
			card_name = scryfall_card['name']
			do_process_card = True
			# Matches the given card to its corresponding object in the bulk data using the parameterized method
			for method in match_methods:
				if not method(scryfall_card):
					do_process_card = False
					# If one match does not go through, break out of matching
					break

			if do_process_card:
				# Processes bulk data object for output using the parameterized method
				if not processor_method(scryfall_card, scanned_cards):
					failed_cards.append(scryfall_card)

		except Exception as E:
			print(f"Errant operation parsing card {scryfall_card['name']}")
			print(E)
			failed_cards.append(scryfall_card)

	# Outputs success / failure
	if len(scanned_cards) > 0:
		print(f"Success! Found {len(scanned_cards)} cards")
	else:
		print("Failure! No cards found!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")
		print(failed_cards)

	return scanned_cards


def controller_test_count():
	print("Counting cards")
	data = controller_get_data()
	cards = scan_bulk_data_list(data, [scan_card_is_eternal], scanner_longest_name)
	write_data(cards)


def controller_get_data():
	# Import each printing of each card
	data = import_scryfall_abridged()
	print("Imported cards!")
	return data


if __name__ == '__main__':
	print("Scanning Scryfall data!")
	controller_test_count()
