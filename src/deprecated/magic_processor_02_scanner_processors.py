from common_methods_grinder import *


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


# Outputs non printing-specific information. To wit:
# name -      input
# card_type - output
# color_id -  output
# colors -    output
def scanner_get_card_name_data(scryfall_card, scanned_cards):
	try:
		new_line = {'name': scryfall_card['name'],
		            "color_id": get_color_code_from_colors(scryfall_card["color_identity"]),
		            "colors": get_color_code_from_colors(get_field_from_card("colors", scryfall_card, not_found="")),
		            "type_line": get_field_from_card("type_line", scryfall_card, not_found=""),
		            "type": get_card_type_from_type_line(get_field_from_card("type_line", scryfall_card, not_found="")),
		            "cmc": get_field_from_card("cmc", scryfall_card, not_found=-1),
		            "mana_cost": get_field_from_card("mana_cost", scryfall_card, not_found="none"),
		            "edhrec_rank": get_field_from_card("edhrec_rank", scryfall_card, not_found=-1)}

		produced_mana = get_field_from_card("produced_mana", scryfall_card, not_found="none")
		if produced_mana != "none":
			new_line["produced_mana"] = get_color_code_from_colors(produced_mana)
		else:
			new_line["produced_mana"] = ""

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


# Counts each mana value
# Histogram - empty dictionary
def histogram_sort_mana_costs(scryfall_card, histogram):
	try:
		# name = scryfall_card['name']

		if "card_faces" in scryfall_card:
			for face in scryfall_card["card_faces"]:
				if "mana_cost" in face:
					sort_mana_costs_processor(face["mana_cost"], histogram, face["name"])
				else:
					return False
		elif "mana_cost" in scryfall_card:
			sort_mana_costs_processor(scryfall_card["mana_cost"], histogram, scryfall_card['name'])
		else:
			return False

		# if "mana_cost" in scryfall_card:
		# 	mana_cost = scryfall_card["mana_cost"]
		# elif "mana_cost" in scryfall_card["card_faces"][0]:
		# 	mana_cost = scryfall_card["card_faces"][0]["mana_cost"]
		# else:
		# 	mana_cost = ""

		return True

	except Exception as E:
		print("Errant operation scanning card!")
		print(E)
		return False


def sort_mana_costs_processor(mana_cost, histogram, name):
	if mana_cost in histogram:
		histogram[mana_cost].append(name)
	else:
		histogram[mana_cost] = [name]

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
