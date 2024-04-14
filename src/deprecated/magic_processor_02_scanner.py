from common_methods_io import write_data, write_data_dictionary
# from shared_methods_grinder import get_all_creature_types
from import_scryfall_bulk_data import *

from magic_processor_02_scanner_scan_methods import *
from magic_processor_02_scanner_processors import *
from magic_processor_02_match_data_processors import *


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


# Outputs all cards from a given dataset using the given processor method
# Requires unsorted data
def get_set_cards(data, processor_method, set_name):
	bound_cards = []
	failed_cards = []

	for scryfall_card in data:
		if scryfall_card["set"] == set_name.lower():
			card = {}
			if processor_method(scryfall_card, card):
				bound_cards.append(card)
			else:
				print("Binding card failed!")
				failed_cards.append(card)

	print(f"{len(failed_cards)} failed")
	print(f"{len(bound_cards)} bound")

	def sort_collector_num(e):
		return int(e["collector_number"])

	bound_cards.sort(key=sort_collector_num)

	return bound_cards


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


def controller_get_set_unique_card_field(field="set_type"):
	print("Finding each set type")
	data = controller_get_data()
	match_methods = [scan_card_is_eternal, scan_card_is_paper]
	all_set_types = scan_bulk_data_set(data, match_methods, set_find_string_field, field)
	print(all_set_types)


def controller_get_unique_mana_costs():
	print("Finding each unique mana cost")
	data = controller_get_data()
	# match_methods = [scan_card_is_eternal, scan_card_is_paper]
	match_methods = []
	all_mana_values = scan_bulk_data_histogram(data, match_methods, histogram_sort_mana_costs)
	# print(all_mana_values)
	mana_value_totals = {}
	cards_with_unique_mv = 0

	for key in all_mana_values:
		count = len(all_mana_values[key])
		mana_value_totals[key] = count
		if count == 1:
			# print(f"{all_mana_values[key][0]} | {key}")
			print(all_mana_values[key][0])
			cards_with_unique_mv += 1

	print(f"Total cards with unique mana values: {cards_with_unique_mv}")
	return mana_value_totals


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


def controller_create_set_sheet(set_name="DMU"):
	print(f"Creating set sheet for set {set_name}")
	data = import_scryfall_full()
	set_sheet = get_set_cards(data, get_set_sheet, set_name)

	write_data(set_sheet)


if __name__ == '__main__':
	print("Scanning Scryfall data!")
	mana_values = controller_get_unique_mana_costs()
	write_data_dictionary(mana_values)
