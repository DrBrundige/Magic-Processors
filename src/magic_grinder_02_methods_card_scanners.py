# Creates a simple list of all cards.
def scanner_count_cards(scryfall_card, scanned_cards):
	try:
		new_line = {'name': scryfall_card['name'], 'set': scryfall_card['set'],
		            'set_num': scryfall_card['collector_number']}
		scanned_cards.append(new_line)
		return True
	except Exception as E:
		print("Errant operation scanning card!")
		print(E)
		return False


# Scans to fine the card with the longest name.
def scanner_longest_name(scryfall_card, scanned_cards):
	try:
		if 'card_faces' in scryfall_card:
			for face in scryfall_card['card_faces']:
				new_line = {'name': face['name'], 'set': scryfall_card['set'],
				            'set_num': scryfall_card['collector_number'], 'length': len(face['name'])}
				scanned_cards.append(new_line)
		else:
			new_line = {'name': scryfall_card['name'], 'set': scryfall_card['set'],
			            'set_num': scryfall_card['collector_number'], 'length': len(scryfall_card['name'])}
			scanned_cards.append(new_line)
		return True
	except Exception as E:
		print("Errant operation scanning card!")
		print(E)
		return False


# # # # # # # # # # #
# HISTOGRAM METHODS #
# # # # # # # # # # #

# Counts each card name
# Histogram - empty dictionary
def histogram_count_card_names(scryfall_card, histogram):
	try:
		name = scryfall_card['name']
		if name in histogram:
			histogram[name] = histogram[name] + 1
		else:
			histogram[name] = 1

		return True

	except Exception as E:
		print("Errant operation scanning card!")
		print(E)
		return False


# Counts each creature type if the face is legendary.
# Histogram - preloaded with each creature type
def histogram_legendary_creature_types(scryfall_card, histogram):
	try:
		if 'card_faces' in scryfall_card:
			for face in scryfall_card['card_faces']:
				if "Legendary" in face["type_line"]:
					for type in face["type_line"].split():
						if type in histogram:
							histogram[type] = histogram[type] + 1
		else:
			for type in scryfall_card["type_line"].split():
				if "Legendary" in scryfall_card["type_line"]:
					if type in histogram:
						histogram[type] = histogram[type] + 1
		return True

	except Exception as E:
		print("Errant operation scanning card!")
		print(E)
		return False


# # # # # # # #
# SET METHODS #
# # # # # # # #

def set_find_string_field(scryfall_card, fields_set, field):
	try:
		if field in scryfall_card:
			if scryfall_card[field] not in fields_set:
				fields_set.add(scryfall_card[field])
			return True
		else:
			return False
	except Exception as E:
		print("Errant operation scanning card!")
		print(E)
		return False


def set_find_string_list(scryfall_card, fields_set, field):
	try:
		if field in scryfall_card:
			for field_item in scryfall_card[field]:
				if field_item not in fields_set:
					fields_set.add(field_item)
			return True
		else:
			return False
	except Exception as E:
		print("Errant operation scanning card!")
		print(E)
		return False
