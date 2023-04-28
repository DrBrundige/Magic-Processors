from shared_methods_io import write_data, read_csv
from import_scryfall import import_scryfall_abridged, import_scryfall_art, import_scryfall_full
from sort_card_data import sort_cards_by_set

from magic_grinder_02_methods_card_processors import *
from magic_grinder_02_methods_custom_match import *


# Data - Requires the full default-cards dataset sorted with the sort_cards_by_set
# Inputs cards from a bulk set sheet: name, count (optional), foil, collector_number, set
def match_bulk_data(data_sorted, all_cards, match_method, processor_method, do_output_count=False):
	bound_cards = []
	failed_cards = []

	# Iterates through each card in the all_cards list
	for card in all_cards:
		try:

			# Some input files include a count row. If this row exists and is equal to 0, skips the card
			if 'count' in card and int(card['count']) <= 0:
				continue

			# Matches the given card to its corresponding object in the bulk data using the parameterized method
			scryfall_card = match_method(data_sorted, card)

			if scryfall_card is None:
				print("Errant operation! Could not find card: " + card['name'])
				failed_cards.append(card)
				continue

			# Processes bulk data object for output using the parameterized method
			new_line = processor_method(scryfall_card, card)

			# Some input files include a count row. If this row exists and is greater than 1,
			#     adds the row to the output list that number of times. Otherwise adds it once.
			if do_output_count and ('count' in card and int(card['count']) > 1):
				for i in range(int(card['count'])):
					bound_cards.append(new_line)
			else:
				bound_cards.append(new_line)

		except Exception as E:
			print(f"Errant operation parsing card {card['name']}")
			print(E)
			failed_cards.append(card)

	# Outputs success / failure
	if len(bound_cards) > 0:
		print(f"Success! Bound {len(bound_cards)} cards")
	else:
		print("Failure! No cards bound!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")
		print(failed_cards)

	return bound_cards


def controller_value_collection():
	print("Valuing collection")

	prices = match_bulk_data(controller_get_sorted_data(), read_csv("card_library_dmu.csv"), standard_match_full,
	                         get_card_usd)
	write_data(prices, "prices")


def controller_get_audit_from_set_sheet(filename = "all_order_cards_full.csv"):
	print("Matching cards to audit data")

	audit_rows = match_bulk_data(controller_get_sorted_data(), read_csv(filename),
	                             standard_match_full, get_audit_row, do_output_count=False)
	write_data(audit_rows, "audit")


def controller_get_set_number_from_variant():
	print("Getting set number")
	audit_rows = match_bulk_data(controller_get_sorted_data(), read_csv("all_extra_trade_cards.csv"),
	                             full_match_no_set_num, get_audit_row)
	write_data(audit_rows)


# Returns the unabridged dataset sorted by set code
def controller_get_sorted_data():
	# Import each printing of each card
	then = datetime.now().timestamp()
	data = import_scryfall_full()
	print("Imported cards!")
	# Sorts all cards into a dictionary by set
	data_sorted = sort_cards_by_set(data)
	now = datetime.now().timestamp()
	print(f"Sorted cards! Imported and sorted {len(data)} cards in {now-then} seconds!")
	return data_sorted


if __name__ == '__main__':
	print("Processing Bulk Data")
	controller_get_audit_from_set_sheet("all_audit_reset_cards.csv")
