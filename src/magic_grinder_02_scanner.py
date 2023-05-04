from shared_methods_io import write_data, write_data_dictionary
from shared_methods_grinder import get_all_creature_types
from import_scryfall import import_scryfall_abridged, import_scryfall_art, import_scryfall_full
from sort_card_data import sort_cards_by_set

from magic_grinder_02_methods_custom_scan import *
from magic_grinder_02_methods_card_scanners import *


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
					failed_cards.append(scryfall_card['name'])

		except Exception as E:
			print(f"Errant operation parsing card {scryfall_card['name']}")
			print(E)
			failed_cards.append(scryfall_card['name'])

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


# Scans bulk data (either full or abridged) and outputs cards in a list.
#    Unlike the bulk matcher, accepts multiple matching methods
def scan_bulk_data_histogram(data, match_methods, processor_method, histogram=None):
	if histogram is None:
		histogram = {}

	failed_cards = []
	total_counted_cards = 0

	for scryfall_card in data:
		try:
			# card_name = scryfall_card['name']
			do_process_card = True
			# Matches the given card to its corresponding object in the bulk data using the parameterized method
			for method in match_methods:
				if not method(scryfall_card):
					do_process_card = False
					# If one match does not go through, break out of matching
					break

			if do_process_card:
				# Processes bulk data object for output using the parameterized method
				if not processor_method(scryfall_card, histogram):
					failed_cards.append(scryfall_card['name'])
				else:
					total_counted_cards += 1

		except Exception as E:
			print(f"Errant operation parsing card {scryfall_card['name']}")
			print(E)
			failed_cards.append(scryfall_card['name'])

	# Outputs success / failure
	if total_counted_cards > 0:
		print(f"Success! Counted {total_counted_cards} cards")
	else:
		print("Failure! No cards counted!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")
		print(failed_cards)

	return histogram


# I think this scans for non-card data, such as set types
def scan_bulk_data_set(data, match_methods, processor_method, field):
	fields_set = set()
	failed_cards = []
	total_counted_cards = 0

	for scryfall_card in data:
		try:
			# card_name = scryfall_card['name']
			do_process_card = True
			# Matches the given card to its corresponding object in the bulk data using the parameterized method
			for method in match_methods:
				if not method(scryfall_card):
					do_process_card = False
					# If one match does not go through, break out of matching
					break

			if do_process_card:
				# Processes bulk data object for output using the parameterized method
				if not processor_method(scryfall_card, fields_set, field):
					failed_cards.append(scryfall_card['name'])
				else:
					total_counted_cards += 1

		except Exception as E:
			print(f"Errant operation parsing card {scryfall_card['name']}")
			print(E)
			failed_cards.append(scryfall_card['name'])

	# Outputs success / failure
	if total_counted_cards > 0:
		print(f"Success! Counted {total_counted_cards} cards")
	else:
		print("Failure! No cards counted!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")
		print(failed_cards)

	return fields_set


def controller_test_count():
	print("Counting cards")
	data = controller_get_data()
	cards = scan_bulk_data_list(data, [scan_card_is_eternal], scanner_longest_name)
	write_data(cards)


# Outputs non printing-specific information, such as color and card type
def controller_get_card_name_data():
	this_data = import_scryfall_abridged()
	all_card_names = scan_bulk_data_list(this_data, [scan_card_is_eternal], scanner_get_card_name_data)
	write_data(all_card_names, "card_names")


def controller_get_legendary_creatures_histogram():
	print("Counting legendary creatures")
	data = controller_get_data()
	histogram = controller_create_type_histogram()
	match_methods = [scan_card_is_eternal, scan_card_is_paper]
	all_types = scan_bulk_data_histogram(data, match_methods, histogram_legendary_creature_types, histogram)
	write_data_dictionary(all_types, "types")


# Grinds the dataset for each unique art, counting the cards with the most arts.
def controller_get_unique_arts_histogram():
	data = import_scryfall_art()
	histogram = {}
	match_methods = [scan_card_is_paper]
	all_arts = scan_bulk_data_histogram(data, match_methods, histogram_count_card_names, histogram)
	write_data_dictionary(all_arts, "arts")

	print("Imported cards!")


def controller_get_set_unique_card_set_types():
	print("Finding each set type")
	data = controller_get_data()
	match_methods = [scan_card_is_eternal, scan_card_is_paper]
	all_set_types = scan_bulk_data_set(data, match_methods, set_find_string_field, "set_type")
	print(all_set_types)


def controller_get_all_card_data():
	data = controller_get_data()


# write_data_dictionary(all_set_types, "types")

# Retrieves abridged data
def controller_get_data():
	# Import each printing of each card
	data = import_scryfall_abridged()
	print("Imported cards!")
	return data


# Creates an empty histogram for each creature type listed in the CR
def controller_create_type_histogram():
	histogram = {}
	all_types = get_all_creature_types()
	for type in all_types:
		histogram[type] = 0

	return histogram


if __name__ == '__main__':
	print("Scanning Scryfall data!")
	controller_get_card_name_data()
