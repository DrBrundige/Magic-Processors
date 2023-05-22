from magic_sorter import MagicSorterTrie
from shared_methods_io import read_json, read_csv, write_data


def assign_default_section(card):
	# This calculates whether the card is in a set box
	if int(card["box_code"]) < 20:
		return card["price_range"]
	# Logic for basic lands box
	if card["home_box"] == "Lands":
		id = card["color_id"]
		if id == "W":
			return "21 - White"
		elif id == "U":
			return "22 - Blue"
		elif id == "B":
			return "23 - Black"
		elif id == "R":
			return "24 - Red"
		elif id == "G":
			return "25 - Green"
	# Logic for Commander box, etc.
	color = card["colors"]
	if color != "C":
		if len(color) > 1:
			return "31 - Multicolor"
		elif color == "W":
			return "21 - White"
		elif color == "U":
			return "22 - Blue"
		elif color == "B":
			return "23 - Black"
		elif color == "R":
			return "24 - Red"
		elif color == "G":
			return "25 - Green"
	elif "Artifact" in card["card_type"]:
		if card["card_type"] == "Artifact Creature":
			return "41 - Artifact (Artifact Creature)"
		elif card["card_type"] == "Artifact Equipment":
			return "43 - Artifact (Equipment)"
		elif len(card["produced_mana"]) > 0:
			return "42 - Artifact (Mana Rock)"
		else:
			return "44 - Artifact (Utility Artifact)"
	elif "Land" in card["card_type"]:
		if len(card["produced_mana"]) > 1:
			return "52 - Color Fixing Lands"
		else:
			return "51 - Utility Lands"
	else:
		return "11 - Colorless"


def assign_price_range(card, high_value=2):
	try:
		if float(card["value"]) > high_value:
			return "01 - Rares"
		elif card["rarity"] == "R" or card["rarity"] == "M":
			return "02 - Bulk Rares"
		else:
			return "03 - Bulk Commons"
	except ValueError as V:
		print("Value error calculating price range. Blanking card['value']")
		card["value"] = "0"
		return assign_price_range(card, high_value)


if __name__ == '__main__':
	print("Sorting card collection")
	SortAudit = MagicSorterTrie("sorter_logic.json")

	all_sort_cards = read_csv("audit_csv.csv", True, True)
	for card in all_sort_cards:
		print(f"Sorting card {card['name']}")
		card["price_range"] = assign_price_range(card, 2)
		card["section"] = assign_default_section(card)
		SortAudit.add_card(card)

	# print(SortAudit)
	all_sorted_cards = SortAudit.output_cards()
	print(len(all_sorted_cards))
	new_id = 1
	for card in all_sorted_cards:
		card["new id"] = new_id
		new_id += 1
	write_data(all_sorted_cards, "reorder")
