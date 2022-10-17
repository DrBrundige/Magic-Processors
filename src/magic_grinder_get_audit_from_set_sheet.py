import cool_stuff
from magic_grinder_get_card_features import *
from sort_card_data import sort_cards_by_set


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
def bind_card_list_audit(data_set, source_cards="all_audit_cards.csv"):
	all_cards = cool_stuff.read_csv(source_cards)
	bound_cards = []
	failed_cards = []

	for card in all_cards:

		if int(card['count']) <= 0:
			continue

		scryfall_card = next(
			(item for item in data_set[card['set'].lower()] if
			 item['name'] == card['name'] and item['collector_number'] == card['collector_number']), None)

		if scryfall_card is None:
			print("Errant operation! Could not find card: " + card['name'])
			failed_cards.append(card['name'])
			continue

		new_line = {'name': card['name'], 'id': '', 'set': scryfall_card['set'].upper(),
		            'set_num': scryfall_card['collector_number'],
		            'is_foil': card['foil'], "variant": get_card_variant(scryfall_card)}

		if new_line["variant"].find("Frame") > -1:
			new_line["spc"] = 0
		else:
			new_line["spc"] = 1

		new_line["home_box"] = ""
		new_line["location"] = ""
		new_line["section"] = ""
		new_line["box_code"] = ""

		new_line["year"] = scryfall_card["released_at"][0:4]
		new_line["rarity"] = scryfall_card["rarity"][0].upper()
		new_line["card_type"] = get_card_type(scryfall_card["type_line"])
		new_line["color_id"] = get_card_id_code(scryfall_card["color_identity"])

		# print(new_line)
		for i in range(int(card['count'])):
			bound_cards.append(new_line)

	if len(failed_cards) == 0:
		print("Success! No cards failed!")
	else:
		print(f"Failed with {len(failed_cards)} card(s)!")
		print(failed_cards)
	return bound_cards


if __name__ == '__main__':
	print("Get audit from set sheet")

	# Import each printing of each card
	data = import_scryfall("default-cards-20220919210802.json")
	print("Imported cards!")
	data = sort_cards_by_set(data)
	print("Sorted cards!")

	audit_cards = bind_card_list_audit(data, "card_library_dmu.csv")
	cool_stuff.write_data(audit_cards, "audit")
