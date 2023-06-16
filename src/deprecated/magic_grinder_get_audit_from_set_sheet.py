from ..shared_methods_grinder import *
from src.deprecated.sort_card_data import sort_cards_by_set
from ..import_scryfall import import_scryfall_full
from datetime import datetime


# Inputs cards from a bulk set sheet. name, count, foil, collector_number, set
# Outputs rows for audit sheet. To wit:
# name - input
# id - empty
# set - input
# set_num - input
# is_foil - input
# variant - output
# spc - output
# home_box - empty
# location - empty
# section - empty
# box_code - empty
# year - output
# rarity - output
# card_type - output
# color_id - output
# Data - Requires the full default-cards dataset sorted with the sort_cards_by_set
def bind_card_list_audit(data_sorted, source_cards="all_audit_cards.csv"):
	# Reads cards from reference. Initializes empty lists.
	all_cards = cool_stuff.read_csv(source_cards)
	bound_cards_audit = []  # List of card objects as dictionaries
	failed_cards = []  # List of names of failed cards as strings

	for card in all_cards:
		try:

			# The Count column notes how many of a card are in the collection.
			#    If this value is 0 or less, skips the card
			if int(card['count']) <= 0:
				continue

			# Matches a card with its Scryfall object by searching the set for the card with that collector's number
			scryfall_card = next(
				(item for item in data_sorted[card['set'].lower()] if
				 item['name'] == card['name'] and item['collector_number'] == card['collector_number']), None)

			# If no card object is matched, adds card to list of failed cards
			if scryfall_card is None:
				print("Errant operation! Could not find card: " + card['name'])
				failed_cards.append(card['name'])
				continue

			# Creates a new Audit row from the matched card data
			new_line = {'name': card['name'], 'id': '', 'set': scryfall_card['set'].upper(),
			            'set_num': scryfall_card['collector_number'],
			            'is_foil': card['foil'], "variant": get_card_variant(scryfall_card)}

			# The spc column notes whether a card has a special collectible treatment.
			#    Cards with no such treatment are noted in the variant column as '2015 Frame'
			if "Frame" in new_line["variant"]:
				new_line["spc"] = 0
			else:
				new_line["spc"] = 1

			# These lines will be calculated once transferred to Excel
			new_line["home_box"] = ""
			new_line["location"] = ""
			new_line["section"] = ""
			new_line["box_code"] = ""

			# new_line["year"] = scryfall_card["released_at"][0:4]
			new_line["year"] = str(datetime.today().year)
			new_line["rarity"] = scryfall_card["rarity"][0].upper()
			new_line["card_type"] = get_card_type_from_type_line(scryfall_card["type_line"])
			new_line["color_id"] = get_color_code_from_colors(scryfall_card["color_identity"])

			# Adds a number of copies to the output list equal to the value of the Count
			#     column in the input
			for i in range(int(card['count'])):
				bound_cards_audit.append(new_line)

		except Exception as E:
			print(f"Errant operation processing card {card['name']}")
			print(E)
			failed_cards.append(card['name'])

	# Outputs success / failure
	if len(bound_cards_audit) > 0:
		print(f"Success! Bound {len(bound_cards_audit)} cards")
	else:
		print("No cards bound!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")
		print(failed_cards)

	return bound_cards_audit


if __name__ == '__main__':
	print("Get audit from set sheet")

	# Import each printing of each card
	data = import_scryfall_full()
	print("Imported cards!")
	data_sorted = sort_cards_by_set(data)
	print("Sorted cards!")

	audit_cards = bind_card_list_audit(data_sorted, "all_audit_cards_dmu.csv")
	cool_stuff.write_data(audit_cards, "audit")
