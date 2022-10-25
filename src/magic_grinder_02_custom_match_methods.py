from unidecode import unidecode
from shared_methods_grinder import get_card_variant


# The standard matching algorithm for full bulk data. Matches by set, then name and set number
# Requires set, name, and set number
def standard_match_full(data_sorted, card):
	if card['set'].lower() not in data_sorted.keys():
		print(f"Errant operation! Could not find set {card['set']} for card {card['name']}")
		return None

	return next(
		(item for item in data_sorted[card['set'].lower()] if
		 unidecode(item['name']) == unidecode(card['name'])
		 and item['collector_number'] == card['collector_number']), None)


# Finds a bulk item where no set number is confirmed. Matches by set, then tries to match by name.
#     If two or more names are found, matches by frame
# Requires set, name, and frame
def full_match_no_set_num(data_sorted, card):
	if card['set'].lower() not in data_sorted.keys():
		print(f"Errant operation! Could not find set {card['set']} for card {card['name']}")
		return None

	this_set = data_sorted[card['set'].lower()]

	cards_matching_name = []

	for bulk_card in this_set:
		if unidecode(bulk_card['name']) == unidecode(card['name']):
			cards_matching_name.append(bulk_card)

	if len(cards_matching_name) == 1:
		return cards_matching_name[0]
	else:
		if 'frame' not in card:
			print(f"Input card {card['name']} has no frame value!")
			return None
		for bulk_card in cards_matching_name:
			bulk_frame = get_card_variant(bulk_card)
			if bulk_frame == card['frame']:
				return bulk_card

	return None


# return next(
# 	(item for item in data_sorted[card['set'].lower()] if
# 	 unidecode(item['name']) == unidecode(card['name'])
# 	 and get_card_variant(item) == card['frame']), None)


# Simplest matching algorithm for abridged data. Matches by name.
# Requires name.
def standard_match_abridged(data, card):
	return next(
		(item for item in data if unidecode(item['name']) == unidecode(card['name'])), None)
