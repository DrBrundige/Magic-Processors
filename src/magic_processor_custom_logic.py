from bulk_data_import import *
from common_methods_processor import get_card_is_eternal
from common_methods_processor_03 import sort_cards_by_set_num
from magic_processor_03 import get_all_cards_from_data_file, output_bound_cards
from common_methods_io import write_data_list


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

		if not (any_card_is_triangle(all_cards=cards_with_name) and any_card_is_non_triangle(all_cards=cards_with_name)):
			continue

		sorted_cards = sort_cards_by_set_num(cards_with_name)
		sorted_cards.sort(key=sort_release)

		if "security_stamp" in sorted_cards[0] and sorted_cards[0]["security_stamp"] == "triangle":
			print(f"Found card first printed in triangle: {card_name}")
			card_details.append(sorted_cards[len(sorted_cards)-1])

	sorted_card_details = sort_cards_by_set_num(card_details)
	sorted_card_details.sort(key=sort_release)

	card_objects = get_all_cards_from_data_file(sorted_card_details)
	match_fields = ["name", "flavor_name", "set", "set_num", "released_at", "mana_cost", "security_stamp"]
	output_rows = output_bound_cards(card_objects, match_fields)
	output_rows.insert(0, match_fields)
	write_data_list(output_rows, "real_reprint")
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
	controller_find_crossovers_with_real_magic_reprint()
