# Magic Grinder Thomas Brundige Jones 2021

# import requests
import math
from magic_call_scryfall import call_scryfall_creature_types

import cool_stuff
from magic_grinder_get_card_features import *


# For a given list of card names, returns additional information about each card
#    Returns rarity, scryfall uri, type line, mana cost, and color id
# Note: Card names are case and special-character sensitive.
def bind_card_list(source_cards="all_paper_cards.csv", scryfall_source="oracle-cards-20210712.json"):
	all_cards = cool_stuff.read_csv_list(source_cards)
	data = import_scryfall(scryfall_source)
	bound_cards = []
	failed_cards = []

	for card in all_cards:
		# print(card)
		scryfall_card = next((item for item in data if item['name'] == card), None)
		if scryfall_card is None:
			print("Errant operation! Could not find card: " + card)
			failed_cards.append(card)
			continue
		new_line = {'name': card, 'rarity': scryfall_card['rarity'].capitalize(),
		            'scryfall_uri': scryfall_card['scryfall_uri'], 'cmc': int(scryfall_card['cmc'])}

		if 'card_faces' in scryfall_card:
			new_line['type_line'] = get_card_type(scryfall_card['card_faces'][0]['type_line'])
			new_line['mana_cost'] = scryfall_card['card_faces'][0]['mana_cost']
		else:
			new_line['type_line'] = get_card_type(scryfall_card['type_line'])
			new_line['mana_cost'] = scryfall_card['mana_cost']

		id = ""
		for color in scryfall_card['color_identity']:
			id += color
		new_line['id'] = id

		print(f"Success! Found {card}")
		bound_cards.append(new_line)
	if len(failed_cards) == 0:
		print("Success! No cards failed!")
	else:
		print(f"Failed with {len(failed_cards)} card(s)!")
		print(failed_cards)
	return bound_cards


# For a given list of card names, returns additional information needed to print a paper card
#    Returns name, mana cost, type, rules text, and flavor text
# Note: Card names are case and special-character sensitive.
def bind_card_list_printout(data, source_cards="all_paper_cards.csv"):
	all_cards = cool_stuff.read_csv_list(source_cards)
	bound_cards = []
	failed_cards = []

	attributes = ['name', 'mana_cost', 'type_line', 'oracle_text', 'power', 'toughness', 'flavor_text']

	for card in all_cards:
		print(card)
		scryfall_card = next((item for item in data if item['name'] == card), None)
		if scryfall_card is None:
			print("Errant operation! Could not find card: " + card)
			failed_cards.append(card)
			continue

		# If card has multiple faces, add line for each face
		if 'card_faces' in scryfall_card:
			for face in scryfall_card['card_faces']:
				new_line = extract_card_data(face, attributes)
				print(new_line)
				bound_cards.append(new_line)
		else:
			new_line = extract_card_data(scryfall_card, attributes)
			print(new_line)
			bound_cards.append(new_line)
	if len(failed_cards) == 0:
		print("Success! No cards failed!")
	else:
		print(f"Failed with {len(failed_cards)} card(s)!")
		print(failed_cards)
	return bound_cards


# For a given list of card names and set, returns collector's number
# Note: Card names are case and special-character sensitive.
def bind_card_list_audit(source_cards="all_audit_cards.csv", scryfall_source="default-cards-20220109220253.json"):
	all_cards = cool_stuff.read_csv(source_cards)
	data = import_scryfall(scryfall_source)
	bound_cards = []
	failed_cards = []

	for card in all_cards:
		# print(card)
		# is_showcase = True if card['is_showcase'] == '0' else False

		scryfall_card = next(
			(item for item in data if item['name'] == card['name'] and item['set'] == card['set'].lower()), None)

		# scryfall_card = next((item for item in data if
		#                       item['name'] == card['name'] and item['set'] == card['set'] and item[
		# 	                      'booster'] == is_showcase), None)
		if scryfall_card is None:
			print("Errant operation! Could not find card: " + card['name'])
			failed_cards.append(card['name'])
			continue
		new_line = {'name': card['name'], 'id': card['id'], 'set': card['set'],
		            'col no': scryfall_card['collector_number']}

		print(new_line)
		bound_cards.append(new_line)
	if len(failed_cards) == 0:
		print("Success! No cards failed!")
	else:
		print(f"Failed with {len(failed_cards)} card(s)!")
		print(failed_cards)
	return bound_cards


# Scans a dataset for cards with a given name and set
def find_printing_data(source_cards="all_audit_cards.csv", card_name="", set=""):
	data = import_scryfall(source_cards)
	bound_cards = []
	for scryfall_card in data:
		if scryfall_card['name'] == card_name and (set == "" or scryfall_card['set'] == set):
			bound_cards.append(scryfall_card)
			print(f"Found printing for card {card_name}")

	return bound_cards


# I would hypothesize that this scans a dataset for standard printings of cards, but it doesn't return anything
def find_booster_cards():
	data = import_scryfall("default-cards-20220109220253.json")
	scryfall_card = next((item for item in data if item['booster']), None)
	print(scryfall_card)


# For a single card, extracts a number of attributes into a single line object
def extract_card_data(card_object, attributes):
	new_line = {}
	for attribute in attributes:
		if attribute in card_object:
			new_line[attribute] = str(card_object[attribute])
		else:
			new_line[attribute] = ""

	return new_line


# For a library dataset, reformats as audit.
def reformat_library_to_audit(source_cards):
	audit = []
	for card in source_cards:
		for i in range(int(card['collection'])):
			audit.append({'Name': card['name'], 'Set No.': card['number']})
	# print(card)
	return audit


# Finds the creature types that appear most frequently.
# Also has the option to return creature types that are legendary only
def find_abundant_types(data, legendaries_only=False, non_legendaries_only=False):
	total_types = 0
	# all_types = get_all_creature_types()
	all_types = call_scryfall_creature_types()
	types_histogram = {}

	# Checks against official list of all creature types.
	# This is important because the NEO shrines have the enchantment type Shrine where a creature type might be expected
	for this_type in all_types:
		types_histogram[this_type] = 0

	for card in data:
		if card['legalities']['vintage'] != 'not_legal':
			# if card['layout'] == "token" and len(card['games']) > 0:
			for face in card['type_line'].split("//"):
				# if "Creature" in face in face:
				if "Creature" in face:
					if legendaries_only and "Legendary" not in face:
						continue
					if non_legendaries_only and "Legendary" in face:
						continue

					i = face.find("—")
					if i < 0:
						continue
					subtype_string = face[i + 1:len(face)]
					for this_type in subtype_string.split(" "):
						clean = this_type.strip()
						if len(clean) > 0 and clean in all_types:
							print(clean)
							total_types += 1
							types_histogram[clean] = types_histogram[clean] + 1

	print(f"Success! Found {total_types} types!")
	return types_histogram


def find_token_cards(data):
	total_types = 0
	all_types = []
	types_histogram = {}
	for card in data:
		if card['layout'] == "token" and len(card['games']) > 0:
			type_line = card["type_line"]
			# print(card["type_line"])
			if "Creature" in type_line:
				i = type_line.find("—")
				if i < 0:
					continue
				subtype_string = type_line[i:len(type_line)]
				print(subtype_string)
	return types_histogram


# For a dataset, returns information on each unique set
def extract_set_names(data):
	all_set_names = []
	set_data = []

	for card in data:
		if card['set'] not in all_set_names:
			all_set_names.append(card['set'])
			this_set = {'set_code': card['set'], 'set_name': card['set_name'], 'set_type': card['set_type'],
			            'is_standard_legal': card['legalities']['standard'] != 'not_legal',
			            'is_modern_legal': card['legalities']['modern'] != 'not_legal',
			            'is_eternal_legal': card['legalities']['commander'] != 'not_legal',
			            'date': card['released_at']}
			set_data.append(this_set)

	return set_data


# For a dataset, returns information on each unique card in a given set
def extract_cards_from_set(data, set):
	set = set.lower()
	all_unique_names = []
	all_cards = []
	for card in data:
		if card['set'] == set and card['name'] not in all_unique_names:
			print(f"Found card! {card['name']}")
			new_line = {'name': card['name'], 'set': card['set'],
			            'col no': card['collector_number'], 'rarity': card['rarity'].capitalize(), 'rank': -1}
			if 'edhrec_rank' in card:
				new_line['rank'] = card['edhrec_rank']

			id = ""
			for color in card['color_identity']:
				id += color
			new_line['id'] = id

			all_unique_names.append(card['name'])
			all_cards.append(new_line)

	return all_cards


# For a dataset, returns information on each unique card in a given set
# Returns a list of dictionaries
def extract_all_cards(data):
	all_unique_names = []
	all_cards = []
	for scryfall_card in data:
		if scryfall_card['name'] not in all_unique_names and scryfall_card['legalities']['commander'] != 'not_legal':
			# print(f"Found card! {scryfall_card['name']}")
			new_line = {'name': scryfall_card['name'], 'set': scryfall_card['set'],
			            'col no': cool_stuff.clean_word_digits(scryfall_card['collector_number']),
			            'rarity': scryfall_card['rarity'].capitalize(),
			            'rank': -1, 'id': get_card_id_code(scryfall_card['color_identity']),
			            'cmc': -1}
			if 'edhrec_rank' in scryfall_card:
				new_line['rank'] = scryfall_card['edhrec_rank']

			if 'cmc' in scryfall_card:
				new_line['cmc'] = scryfall_card['cmc']

			if 'card_faces' in scryfall_card:
				new_line['type_line'] = get_card_type(scryfall_card['card_faces'][0]['type_line'])
				new_line['mana_cost'] = scryfall_card['card_faces'][0]['mana_cost']
			else:
				new_line['type_line'] = get_card_type(scryfall_card['type_line'])
				new_line['mana_cost'] = scryfall_card['mana_cost']

			all_unique_names.append(scryfall_card['name'])
			all_cards.append(new_line)

	return all_cards


# For a dataset, returns information on each unique card in a given set
# Returns a list of dictionaries
# Use this one.
def extract_all_cards_in_all_sets(data):
	all_cards = []
	for scryfall_card in data:
		if scryfall_card['legalities']['commander'] != 'not_legal' and not scryfall_card['promo'] and not scryfall_card[
			'variation']:

			# Skip card if it is not printed in paper
			if not "paper" in scryfall_card["games"]:
				continue

			if scryfall_card["border_color"] == "gold" or scryfall_card["set_type"] == "memorabilia":
				continue

			if scryfall_card["lang"] != "en":
				continue

			card_set = scryfall_card['name'] + "|" + scryfall_card['set']
			# print(f"Found card! {scryfall_card['name']}")
			new_line = {'name': scryfall_card['name'], 'set': scryfall_card['set'].upper(),
			            'col no': cool_stuff.clean_word_digits(scryfall_card['collector_number']),
			            'rarity': scryfall_card['rarity'][0].capitalize(), 'usd': 0.0,
			            'rank': -1, 'id': get_card_id_code(scryfall_card['color_identity']),
			            'cmc': -1, 'released_at': scryfall_card['released_at']}

			if 'edhrec_rank' in scryfall_card:
				new_line['rank'] = scryfall_card['edhrec_rank']

			if 'cmc' in scryfall_card:
				new_line['cmc'] = scryfall_card['cmc']

			new_line['variant'] = get_card_variant(scryfall_card)

			if scryfall_card['nonfoil']:
				denomination = 'usd'
			else:
				denomination = 'usd_foil'
			if scryfall_card['prices'][denomination] is not None:
				new_line['usd'] = math.floor(float(scryfall_card['prices'][denomination]) * 4.0) / 4.0

			if 'card_faces' in scryfall_card:
				new_line['type_line'] = get_card_type(scryfall_card['card_faces'][0]['type_line'])
				new_line['mana_cost'] = scryfall_card['card_faces'][0]['mana_cost']
			else:
				new_line['type_line'] = get_card_type(scryfall_card['type_line'])
				new_line['mana_cost'] = scryfall_card['mana_cost']

			all_cards.append(new_line)

	return all_cards


def extract_legal_card_names(data):
	all_names = []
	for card in data:
		if card['legalities']['vintage'] != 'not_legal':
			# or card['layout'] == 'token' and card['set_type'] != 'memorabilia':
			for name in card['name'].split("//"):
				clean = cool_stuff.clean_word(name)
				if len(clean) > 0:
					all_names.append(clean)
	return all_names


def extract_tokens(data):
	all_names = []
	for card in data:
		if card['layout'] == 'token' and card['set_type'] != 'memorabilia':
			for name in card['name'].split("//"):
				clean = cool_stuff.clean_word(name)
				if len(clean) > 0 and clean not in all_names:
					all_names.append(clean)
	return all_names


#
# def extract_card_types(data):
# 	all_types = []
# 	for card in data:
# 		if card['legalities']['vintage'] != 'not_legal':
# 			for type in card['type_line'].split(" "):
# 				clean = cool_stuff.clean_word(type)
# 				if len(clean) > 0 and clean not in all_types:
# 					all_types.append(clean)
# 					print(clean)
# 	return all_types


def extract_keywords(data):
	all_types = []
	for card in data:
		if card['legalities']['vintage'] != 'not_legal':
			for type in card['keywords']:
				clean = cool_stuff.clean_word(type)
				if len(clean) > 0 and clean not in all_types:
					all_types.append(clean)
					print(clean)
	return all_types


def extract_legendaries_names(data):
	all_names = []
	for card in data:
		if card['legalities']['vintage'] != 'not_legal':
			types = card['type_line'].split(" ")
			if 'Legendary' in types and 'Creature' in types:
				for name in card['name'].split("//"):
					comma = name.find(",")
					# print(comma)
					if comma > 0:
						# print(name[0:comma])
						clean = name[0:comma]
					# print(clean)
					else:
						clean = name
					# print(clean)
					if clean not in all_names:
						all_names.append(clean)
	return all_names


def extract_planewalker_names(data):
	all_names = []
	# all_types = []
	for card in data:
		if card['legalities']['vintage'] != 'not_legal':

			if 'card_faces' in card:
				all_card_types = card['card_faces'][0]['type_line'].split(" ")
			else:
				all_card_types = card['type_line'].split(" ")

			if 'Planeswalker' in all_card_types:
				name = all_card_types[-1]
				if name not in all_names:
					all_names.append(name)
	return all_names


def extract_artists(data):
	all_names = []
	for card in data:
		if card['set_type'] == 'memorabilia' or card['set_type'] == 'funny':
			continue
		new_line = {"set": card["set"], "collector_number": card["collector_number"],
		            "released_at": card["released_at"]}
		if "card_faces" in card:
			for face in card["card_faces"]:
				extract_artist(face, new_line)
				new_line["artist_ids"] = face["artist_id"][0]
				new_line["num_artists"] = len(face["artist_id"])
				copy = new_line.copy()
				all_names.append(copy)
		else:
			extract_artist(card, new_line)
			new_line["artist_ids"] = card["artist_ids"][0]
			new_line["num_artists"] = len(card["artist_ids"])
			copy = new_line.copy()
			all_names.append(copy)

	return all_names


# Identifies each unique artist name
def extract_artist(face, new_line):
	all_keys = ["name", "artist", "illustration_id"]

	for key in all_keys:
		if key in face:
			new_line[key] = face[key]


def extract_all_possible_values(data, key):
	all_key_values = set()
	for card in data:
		if key in card:
			if card[key] not in all_key_values:
				all_key_values.add(card[key])

	return all_key_values


# Extracts all occurrences of a given field, where that field is a list
def extract_all_possible_values_list(data, key):
	all_values = set()

	for card in data:
		if key in card:
			for value in card[key]:
				if value not in all_values:
					all_values.add(value)

	return all_values


def count_planeswalkers(data, names):
	names_dict = {}
	for name in names:
		names_dict[name] = 0

	for card in data:
		if card['legalities']['vintage'] != 'not_legal':
			card_types = ''
			if 'card_faces' in card:
				type_lines = card['card_faces'][0]['type_line'] + " \\ " + card['card_faces'][1]['type_line']
				card_types = type_lines.split(" ")
			else:
				card_types = card['type_line'].split(" ")

			if not 'Planeswalker' in card_types:
				continue

			for type in card_types:
				if type in names:
					names_dict[type] = names_dict[type] + 1

	return names_dict


# Finds oracle text for each card
def extract_oracle_text(data, remove_reminder_text=False):
	all_cards = []
	for card in data:
		if card['legalities']['vintage'] != 'not_legal':
			new_row = {'name': card['name']}
			if "oracle_text" in card:
				if remove_reminder_text:
					oracle_text = get_oracle_text_without_reminder_text(card["oracle_text"])
				else:
					oracle_text = card["oracle_text"]
				new_row["oracle_text"] = oracle_text
			else:
				if remove_reminder_text:
					oracle_text_front = get_oracle_text_without_reminder_text(card["card_faces"][0]["oracle_text"])
					oracle_text_back = get_oracle_text_without_reminder_text(card["card_faces"][1]["oracle_text"])
				else:
					oracle_text_front = card["card_faces"][0]["oracle_text"]
					oracle_text_back = card["card_faces"][1]["oracle_text"]

				new_row["oracle_text"] = oracle_text_front + "\n" + oracle_text_back
			new_row["num_chars"] = len(new_row["oracle_text"])
			new_row["num_words"] = cool_stuff.count_words(new_row["oracle_text"])
			all_cards.append(new_row)
	return all_cards


# Finds oracle text for each card
def extract_oracle_text_per_face(data, remove_reminder_text=False):
	all_cards = []
	for card in data:
		if card['legalities']['vintage'] != 'not_legal':
			if not "card_faces" in card:
				if remove_reminder_text:
					oracle_text = get_oracle_text_without_reminder_text(card["oracle_text"])
				else:
					oracle_text = card["oracle_text"]

				new_row = {'name': card['name'], "oracle_text": oracle_text, "num_chars": len(oracle_text),
				           "num_words": cool_stuff.count_words(oracle_text)}
				all_cards.append(new_row)
			else:
				if remove_reminder_text:
					oracle_text = get_oracle_text_without_reminder_text(card['card_faces'][0]['oracle_text'])
				else:
					oracle_text = card['card_faces'][0]['oracle_text']
				new_row = {'name': f"{card['card_faces'][0]['name']} ({card['name']})", "oracle_text": oracle_text,
				           "num_chars": len(oracle_text),
				           "num_words": cool_stuff.count_words(oracle_text)}
				all_cards.append(new_row)

				if remove_reminder_text:
					oracle_text = get_oracle_text_without_reminder_text(card['card_faces'][1]['oracle_text'])
				else:
					oracle_text = card['card_faces'][1]['oracle_text']

				new_row = {'name': f"{card['card_faces'][1]['name']} ({card['name']})", "oracle_text": oracle_text,
				           "num_chars": len(oracle_text),
				           "num_words": cool_stuff.count_words(oracle_text)}
				all_cards.append(new_row)

	return all_cards


# Finds flavor text for each card
# def extract_flavor_text(data):
# 	all_cards = []
# 	for card in data:
# 		if card['legalities']['vintage'] != 'not_legal':
# 			new_row = {'name': card['name']}
# 			if "card_faces" in card:
# 				new_row["oracle_text"] = card["oracle_text"]
# 			else:
# 				new_row["oracle_text"] = card["card_faces"][0]["oracle_text"] + "\n" + card["card_faces"][1][
# 					"oracle_text"]
# 			new_row["num_chars"] = len(new_row["oracle_text"])
# 			new_row["num_words"] = cool_stuff.count_words(new_row["oracle_text"])
# 			all_cards.append(new_row)
# 	return all_cards


def extract_unique_types(data):
	all_creature_type_lines = set()
	counted_type_lines = {}
	for card in data:
		if card['legalities']['vintage'] != 'not_legal':
			for type in card['type_line'].split("//"):
				face_types = type.split("—")

				for i in range(len(face_types)):
					face_types[i] = face_types[i].strip()

				if "Creature" in face_types:
					print("Found creature")
					if type not in all_creature_type_lines:
						counted_type_lines[type] = 1
						all_creature_type_lines.add(type)
					else:
						counted_type_lines[type] = counted_type_lines[type] + 1
	return counted_type_lines


#
# def count_creatures(data, names):
# 	names_dict = {}
# 	for name in names:
# 		names_dict[name] = 0
#
# 	for card in data:
# 		if card['legalities']['vintage'] != 'not_legal':
# 			card_types = ''
# 			if 'card_faces' in card:
# 				type_lines = card['card_faces'][0]['type_line'] + " \\ " + card['card_faces'][1]['type_line']
# 				card_types = type_lines.split(" ")
# 			else:
# 				card_types = card['type_line'].split(" ")
#
# 			if not 'Creature' in card_types and not 'Legendary' in card_types:
# 				continue
#
# 			for type in card_types:
# 				if type in names:
# 					names_dict[type] = names_dict[type] + 1
#
# 	return names_dict

if __name__ == '__main__':
	print("Testing Magic Grinder!")
	# Import each printing of each card
	data = import_scryfall("default-cards-20220722090459.json")

	# Import one printing of each card
	# data = import_scryfall("oracle-cards-20220616090205.json")

	# Imports some cards
	# data = import_scryfall("some_cards.json")

	print("Data imported")

	all_cards = extract_oracle_text_per_face(data, True)
	cool_stuff.write_data(all_cards)

# all_frames = extract_all_possible_values_list(data, "finishes")
# print(all_frames)
