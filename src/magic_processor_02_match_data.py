from common_methods_io import write_data, read_csv, snake_case_parameter
from common_methods_grinder import format_cards_for_audit_sheet
from import_scryfall_bulk_data import *
# from sort_card_data import sort_cards_by_set

from magic_processor_02_match_data_processors import *
from magic_processor_02_match_data_match_methods import *
from common_methods_io_requests import get_image_from_uri
from common_methods import clean_word


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
			if (processor_method(scryfall_card, card)):
				# Some input files include a count row. If this row exists and is greater than 1,
				#     adds the row to the output list that number of times. Otherwise adds it once.
				if do_output_count and ('count' in card and int(card['count']) > 1):
					for i in range(int(card['count'])):
						bound_cards.append(card)
				else:
					bound_cards.append(card)
			else:
				failed_cards.append(card)

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
	# print(failed_cards)

	return bound_cards


# Outputs all cards from a given dataset using the given processor method
# Requires unsorted data
def get_all_cards(data, processor_method):
	bound_cards = []
	card = {}
	for scryfall_card in data:
		new_line = processor_method(scryfall_card, card)
		bound_cards.append(new_line)

	return bound_cards


def controller_value_collection(filename="all_sort_cards.csv"):
	print("Valuing collection")

	data = read_csv(filename, do_snake_case_names=True, do_standardize_header_names=True)
	prices = match_bulk_data(controller_get_sorted_data(), data, standard_match_full,
	                         get_card_usd)
	write_data(prices, "prices")


def controller_get_audit_from_set_sheet(filename="all_order_cards.csv"):
	print("Matching cards to audit data")

	data = read_csv(filename, do_snake_case_names=True, do_standardize_header_names=True)

	audit_rows = match_bulk_data(controller_get_sorted_data(), data,
	                             full_match_no_set_num, get_audit_row, do_output_count=True)
	format_cards_for_audit_sheet(audit_rows)
	write_data(audit_rows, "audit")


def controller_get_audit_from_audit_sheet(filename="audit_csv.csv"):
	print("Matching cards to audit data")
	all_cards = read_csv(filename, do_snake_case_names=True, do_standardize_header_names=True)
	audit_rows = match_bulk_data(controller_get_sorted_data(), all_cards, standard_match_full, get_audit_row,
	                             do_output_count=False)
	format_cards_for_audit_sheet(audit_rows)
	write_data(audit_rows, "audit")


def controller_get_set_number_from_variant(filename="all_extra_trade_cards.csv"):
	print("Getting set number")
	audit_rows = match_bulk_data(controller_get_sorted_data(), read_csv(filename),
	                             standard_match_full, get_wishlist_row)
	write_data(audit_rows)


def controller_get_card_images(filename="all_progenitus_deck_cards.csv", deck="5c_progenitus"):
	print("Getting card images")
	audit_rows = match_bulk_data(controller_get_sorted_data(), read_csv(filename, True, True),
	                             standard_match_full, get_card_images)
	print("Success! Retrieving images")
	for card in audit_rows:
		get_image_from_uri(card["image_uri"], f"{deck}_{snake_case_parameter(clean_word(card['name']))}.jpg")


def controller_get_card_basic_info(filename="all_decklist_cards.csv"):
	print("Getting card info")

	card_rows = match_bulk_data(import_scryfall_abridged(), read_csv(filename),
	                            standard_match_abridged, get_basic_card_data)
	write_data(card_rows)


if __name__ == '__main__':
	print("Processing Bulk Data")
	# controller_get_audit_from_set_sheet()
	# controller_get_audit_from_audit_sheet()
	# controller_value_collection("audit_csv.csv")
	controller_get_card_basic_info()
