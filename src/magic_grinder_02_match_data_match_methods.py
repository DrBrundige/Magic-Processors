from unidecode import unidecode
from shared_methods_grinder import get_card_variant, scrub_card_name


# The standard matching algorithm for full bulk data. Matches by set, then name and set number
# Requires set, name, and collector_number
def standard_match_full(data_sorted, card):
	try:
		if card['set'].lower() not in data_sorted.keys():
			print(f"Errant operation! Could not find set {card['set']} for card {card['name']}")
			return None

		if 'collector_number' in card:
			set_num_name = 'collector_number'
		else:
			set_num_name = 'set_no'

		return next(
			(item for item in data_sorted[card['set'].lower()] if
			 unidecode(item['name']) == unidecode(card['name'])
			 and item['collector_number'] == card[set_num_name]), None)
	except Exception as E:
		print("Errant operation matching card")
		print(E)
		return None


# Finds a bulk item where no set number is confirmed. Matches by set, then tries to match by name.
#     If two or more names are found, matches by frame
# Requires set, name, and frame
def full_match_no_set_num(data_sorted, card):
	# Verifies card set actually exists
	if card['set'].lower() not in data_sorted.keys():
		print(f"Could not find set {card['set']} for card {card['name']}")
		return None

	# Finds the set with the same set code as the matching card
	this_set = data_sorted[card['set'].lower()]

	# 'scrubs' card name, simplifying complex characters and clearing special chars
	card_name = scrub_card_name(card['name'])

	cards_matching_name = []

	# Iterates through set looking for each card with that card name
	for bulk_card in this_set:
		this_bulk_card_name = scrub_card_name(bulk_card['name'])
		if this_bulk_card_name == card_name:
			cards_matching_name.append(bulk_card)

	# If only a single card with that name exists in the set, return that card
	if len(cards_matching_name) == 1:
		return cards_matching_name[0]
	elif len(cards_matching_name) == 0:
		print(f"Could not find card {card['name']} in set {card['set']}")
		return None
	else:
		# If multiple cards with name are in the set, search by frame
		if 'frame' not in card:
			print(f"Input card {card['name']} has no frame value!")
			return None
		for bulk_card in cards_matching_name:
			bulk_frame = get_card_variant(bulk_card)
			if bulk_frame == card['frame']:
				return bulk_card
	# Card with frame could not be found
	return None


# Simplest matching algorithm for abridged data. Matches by name.
# Requires name.
def standard_match_abridged(data, card):
	return next(
		(item for item in data if unidecode(item['name']) == unidecode(card['name'])), None)
