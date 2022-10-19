# Magic Grinder Thomas Brundige Jones 2022
# Crawls the Scryfall bulk data to find art data about cards

from magic_grinder import import_scryfall, get_card_type
import shared_methods_io


def get_all_prints_per_card(data):
	found_cards = {}
	for card in data:
		if "oracle_id" in card:
			if card["oracle_id"] in found_cards:
				found_cards[card["oracle_id"]]["arts"] = found_cards[card["oracle_id"]]["arts"] + 1
			else:
				new_card = {"name": card["name"], "arts": 1, "set_type": card["set_type"]}

	return found_cards


def get_unique_arts_per_card(data):
	found_cards = {}
	for card in data:
		if "oracle_id" in card:
			if card["oracle_id"] in found_cards:
				# this_card = found_cards[card["oracle_id"]]
				# arts = this_card["arts"]
				found_cards[card["oracle_id"]]["arts"] = found_cards[card["oracle_id"]]["arts"] + 1

			# print(arts)
			else:
				new_card = {"name": card["name"], "arts": 1, "set_type": card["set_type"]}
				if "type_line" in card:
					new_card["type_line"] = get_card_type(card["type_line"])
				else:
					new_card["type_line"] = "Multi-faced"
				found_cards[card["oracle_id"]] = new_card

	return found_cards


def get_unique_arts_per_artist(data):
	found_artists = {}
	for card in data:
		if "card_faces" in card:
			for face in card["card_faces"]:
				extract_face(face, found_artists)
		else:
			extract_face(card, found_artists)

	return found_artists


def extract_face(face, found_artists):
	if "artist_ids" in face:
		artist_ids = face["artist_ids"]
	elif "artist_id" in face:
		artist_ids = [face["artist_id"]]
	else:
		return

	for artist_id in artist_ids:
		if artist_id not in found_artists:
			new_artist = {"name": face["artist"], "unique_illustrations": set()}
			found_artists[artist_id] = new_artist

		this_artist = found_artists[artist_id]

		if "illustration_id" in face and face["illustration_id"] not in this_artist["unique_illustrations"]:
			this_artist["unique_illustrations"].add(face["illustration_id"])


def prepare_artist_for_export(dict):
	all_rows = []
	for key in dict:
		new_row = {"id": key, "name": dict[key]["name"],
		           "unique_illustrations": len(dict[key]["unique_illustrations"])}
		all_rows.append(new_row)

	return all_rows


# Checks that art is unique, if so, increments, then adds to list of found arts

if __name__ == '__main__':
	print("Magic Grinder - Art")
	data = import_scryfall("unique-artwork-20220506090227.json")
	print("Success! Imported JSON")

	# Get arts per artist
	artists = get_unique_arts_per_artist(data)
	# print(artists)
	artist_rows = prepare_artist_for_export(artists)
	# print(artist_rows)
	shared_methods_io.write_data(artist_rows, "artists")

# Get unique arts
# unique_printings = get_unique_arts_per_card(data)
# print(len(unique_printings))
# cool_stuff.write_data(prepare_cards_for_export(unique_printings), "art")
