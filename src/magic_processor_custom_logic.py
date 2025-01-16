from bulk_data_import import *
from magic_processor_03 import get_all_cards_from_data_file, output_bound_cards

from common_methods import clean_word
from common_methods_io import write_data_list
from common_methods_processor import get_card_is_eternal, get_card_is_in_format
from common_methods_processor_03 import sort_cards_by_set_num
from common_methods_requests import scrape_sets_from_format_page

from unidecode import unidecode


# Finds each card where no Real Magic printing exists.
# Output as CSV
# This has an annoying blindspot for a handful of promo cards that are dual-faced with the same card on each side.
# For example, the Creepshow Grimgrin is in the system as "Grimgrin, Corpse-Born // Grimgrin, Corpse-Born."
# I don't know how to fix those short of manually filtering them out. In any case.
def controller_find_cards_without_real_magic_printing():
	# data = controller_get_sorted_data_by_field(path="test-cards-2023")
	data = controller_get_sorted_data_by_field(path="default-cards")

	card_names = []
	card_details = []

	for card_name in data:
		has_triangle_printing = False
		has_non_triangle_printing = False
		triangle_card_details = {}

		# This could be handled in a single line in C# with the Each command. Good thing we're not using C#
		for card in data[card_name]:
			if get_card_is_eternal(card):
				# If the card is eternal and is has the triangle stamp, mark as true. Otherwise break out of this loop
				# There may be a way to modularize this logic, but I'm not sure
				if "security_stamp" in card and card["security_stamp"] == "triangle":
					has_triangle_printing = True
					triangle_card_details = card
				else:
					has_non_triangle_printing = True
					continue

		if has_triangle_printing and not has_non_triangle_printing:
			card_names.append(card_name)
			card_details.append(triangle_card_details)
	# print(card_name)

	card_objects = get_all_cards_from_data_file(card_details)
	match_fields = ["name", "flavor_name", "set", "set_num", "released_at", "mana_cost", "security_stamp",
	                "edhrec_rank"]
	output_rows = output_bound_cards(card_objects, match_fields)
	output_rows.insert(0, match_fields)
	write_data_list(output_rows, "no_real_printing")
	return card_details


# Finds each card originally printed as a crossover that later received a real printing.
def controller_find_crossovers_with_real_magic_reprint():
	# data = controller_get_sorted_data_by_field(path="test-cards-OTJ")
	data = controller_get_sorted_data_by_field(path="default-cards")

	# card_names = []
	card_details = []

	for card_name in data:
		cards_with_name = data[card_name]

		if len(cards_with_name) == 1:
			continue

		if not (any_card_is_triangle(all_cards=cards_with_name) and any_card_is_non_triangle(
				all_cards=cards_with_name)):
			continue

		sorted_cards = sort_cards_by_set_num(cards_with_name)
		sorted_cards.sort(key=sort_release)

		if "security_stamp" in sorted_cards[0] and sorted_cards[0]["security_stamp"] == "triangle":
			print(f"Found card first printed in triangle: {card_name}")
			card_details.append(sorted_cards[len(sorted_cards) - 1])

	sorted_card_details = sort_cards_by_set_num(card_details)
	sorted_card_details.sort(key=sort_release)

	card_objects = get_all_cards_from_data_file(sorted_card_details)
	match_fields = ["name", "flavor_name", "set", "set_num", "released_at", "mana_cost", "security_stamp"]
	output_rows = output_bound_cards(card_objects, match_fields)
	output_rows.insert(0, match_fields)
	write_data_list(output_rows, "real_reprint")
	return True


# Finds each card available in Pioneer that is not on Arena in any version
def controller_find_pioneer_cards_not_on_arena(format="pioneer", game="arena"):
	data = controller_get_sorted_data_by_field(path="default-cards", field="oracle_id")
	all_pioneer_sets_raw = scrape_sets_from_format_page("pioneer")
	all_pioneer_sets = []

	for set in all_pioneer_sets_raw:
		all_pioneer_sets.append(unidecode(set.upper()))

	all_card_names = []
	all_scryfall_cards = []

	for card_oracle_id in data:
		first_card = data[card_oracle_id][0]

		if get_card_is_eternal(first_card):
			is_on_arena = any_card_is_value(data[card_oracle_id], "games", game)
			is_pioneer_legal = get_card_is_in_format(first_card, format)

			if not is_on_arena and is_pioneer_legal:
				first_valid_card = get_first_printing_in_list(data[card_oracle_id], all_pioneer_sets)

				all_card_names.append(first_valid_card["name"])
				all_scryfall_cards.append(first_valid_card)

	# else:
	# 	print(card_oracle_id)

	# print(card_oracle_id)

	card_objects = get_all_cards_from_data_file(all_scryfall_cards)
	match_fields = ["name", "set", "set_num", "released_at", "mana_cost", "edhrec_rank"]
	output_rows = output_bound_cards(card_objects, match_fields)
	output_rows.insert(0, match_fields)
	write_data_list(output_rows, "not_on_arena")
	return all_scryfall_cards


# Finds cards unavailable in paper for a given frame
def controller_find_cards_with_no_frame_printing(frame="2015"):
	data = controller_get_sorted_data_by_field(path="default-cards", field="oracle_id", do_order_by_release=True)

	card_details = []

	for card_oracle in data:
		card_has_frame_printing = False
		for scryfall_card in data[card_oracle]:
			# print(scryfall_card["frame"])
			if "frame" in scryfall_card and scryfall_card["frame"] == frame and "paper" in scryfall_card["games"]:
				# print("Found frame")
				card_has_frame_printing = True
				continue

		if not card_has_frame_printing:
			card_details.append(data[card_oracle][0])

	print("Identified a number of cards")

	card_objects = get_all_cards_from_data_file(card_details)
	match_fields = ["name", "set", "set_num", "released_at", "mana_cost", "frame", "edhrec_rank"]
	output_rows = output_bound_cards(card_objects, match_fields)
	output_rows.insert(0, match_fields)
	write_data_list(output_rows, "no_modern_printing")
	return card_details


# Finds cards with only a single art. There may be a way to handle this with the histogram, but I hate the histogram
def controller_find_cards_with_single_artist():
	data = import_scryfall_art()

	card_histogram = {}

	# Creates a histogram counting the appearances of each card
	for scryfall_card in data:
		if "oracle_id" in scryfall_card and "paper" in scryfall_card["games"]:
			card_name = scryfall_card["oracle_id"]
			if card_name in card_histogram:
				card_histogram[card_name] = card_histogram[card_name] + 1
			else:
				card_histogram[card_name] = 1

	identified_cards = []

	# Loops through data again looking for cards with only one entry
	# lmao I think this is actually the most efficient way to do this
	for scryfall_card in data:
		if "oracle_id" in scryfall_card:
			card_name = scryfall_card["oracle_id"]
			if card_name in card_histogram and card_histogram[card_name] == 1:
				# print(card_name)
				identified_cards.append(scryfall_card)

	# Send identified_cards to processor_03 to process as a bulk data file with given fields
	all_new_cards = get_all_cards_from_data_file(identified_cards)

	match_fields = ["name", "set", "set_num", "released_at", "mana_cost", "artist", "edhrec_rank"]
	output_rows = output_bound_cards(all_new_cards, match_fields)

	output_rows.insert(0, match_fields)
	write_data_list(output_rows, "single_artist")


def get_first_printing_in_list(all_cards, all_valid_sets):
	sorted_card_details = sort_cards_by_set_num(all_cards)
	sorted_card_details.sort(key=sort_set)
	sorted_card_details.sort(key=sort_release)

	for card in sorted_card_details:
		clean_set = unidecode(card["set_name"].upper())
		if clean_set in all_valid_sets:
			return card

	print("Could not find valid set!")
	# If no valid set is found, returns first
	return sorted_card_details[0]


def any_card_is_value(all_cards, field, value):
	for card in all_cards:
		if field in card:
			if value in card[field] or value == card[field]:
				return True
	return False


def all_card_is_value(all_cards, field, value):
	for card in all_cards:
		if field in card:
			if not (value in card[field] or value == card[field]):
				return False
	return True


def any_card_is_triangle(all_cards):
	for card in all_cards:
		if "security_stamp" in card and card["security_stamp"] == "triangle":
			return True
	return False


def any_card_is_non_triangle(all_cards):
	for card in all_cards:
		if not ("security_stamp" in card and card["security_stamp"] == "triangle"):
			return True
	return False


def sort_release(card):
	return card["released_at"]


if __name__ == '__main__':
	print("Processing Magic cards to find complex information.")
	# controller_find_cards_without_real_magic_printing()
	# controller_find_crossovers_with_real_magic_reprint()
	# controller_find_pioneer_cards_not_on_arena()
	# controller_find_cards_with_single_artist()
	controller_find_cards_with_no_frame_printing()

	print("<3")
