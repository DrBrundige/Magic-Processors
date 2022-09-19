# Magic Grinder Thomas Brundige Jones 2022
# Crawls the Scryfall bulk data to find cards first printed at common in a given set

from magic_grinder import import_scryfall
from magic_grinder_get_card_features import prepare_cards_for_export
import cool_stuff


def find_common_cards(data, set="2xm"):
	all_cards = []
	for card in data:
		if card["set"] == set and card["rarity"] == "common":
			# print(card["name"])
			all_cards.append(card["name"])

	return all_cards


def find_first_printing(data, card_names, rarity="common"):
	# All cards that have been found this way
	found_cards = {}
	for card in data:
		# Checks if the current card is a card that we are looking for at the given rarity
		if card["name"] in card_names and card["rarity"] == rarity:
			print(card["name"])
			# Checks if card has been found before
			if card["name"] in found_cards:
				# If card has been found, checks if date is earlier than previous common printing
				if found_cards[card["name"]]["released_at"] > card["released_at"]:
					found_cards[card["name"]]["released_at"] = card["released_at"]
					found_cards[card["name"]]["set"] = card["set"]
					found_cards[card["name"]]["set_name"] = card["set_name"]
			else:
				# If card has not been found, adds to list
				new_row = {"released_at": card["released_at"], "set": card["set"],
				           "set_name": card["set_name"]}
				if "edhrec_rank" in card:
					new_row["edhrec_rank"] = card["edhrec_rank"]
				else:
					new_row["edhrec_rank"] = 0
				found_cards[card["name"]] = new_row

	return found_cards


if __name__ == '__main__':
	print("Magic Grinder Common Printings")
	# Each printing for all cards
	data = import_scryfall("default-cards-20220506090426.json")
	print("Success! Imported JSON")
	all_common_cards = find_common_cards(data, "ima")
	first_common_printing = find_first_printing(data, all_common_cards)

	print(len(first_common_printing))
	prepare_cards_for_export(first_common_printing)
	# cool_stuff.write_data_list(all_common_cards, "card")
	cool_stuff.write_data(prepare_cards_for_export(first_common_printing), "IMA")

# All individual cards
# data = import_scryfall("oracle-cards-20220506090151.json")
