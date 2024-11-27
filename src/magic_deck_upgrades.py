from common_methods_io import read_csv, read_txt, write_data, write_data_dictionary
from common_methods_requests import call_scryfall_03


# Processes a list of card objects into a dictionary histogram
# Accepts a list of dictionaries. Returns a dictionary
def get_audit_card_histogram(all_cards):
	print("Counting cards in collection")
	collection = {}

	for card in all_cards:
		card_name = card["name"]
		if card_name in collection:
			collection[card_name] = collection[card_name] + 1
		else:
			collection[card_name] = 1

	return collection


# Parses a text deck list into dictionary histogram
# Accepts a list of strings. Returns a dictionary
def parse_text_decklist(all_decklist_cards):
	print("Parsing decklist")
	basic_lands = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
	decklist = {}

	for line in all_decklist_cards:
		words = line.split(" ")
		if words[0].isdigit():
			count = int(words.pop(0))
			name = " ".join(words)
			if name not in basic_lands:
				if name not in decklist:
					decklist[name] = count
				else:
					decklist[name] = decklist[name] + count
		else:
			continue

	return decklist


# Accesses a list of cards from the Scryfall API and parses into a dictionary "histogram"
# Accepts a string representing API URL. Returns a dictionary
def get_decklist_from_api(request_url):
	all_request_card_names = set()
	do_get_request_card_names_set(request_url, all_request_card_names)

	decklist = {}

	for name in all_request_card_names:
		decklist[name] = 4

	return decklist


# A recursive method that requests each page from a URL and returns each card name
def do_get_request_card_names_set(request_url, all_reqest_card_names):
	data = call_scryfall_03(request_url)
	# print(data)
	for object in data["data"]:
		all_reqest_card_names.add(object["name"])

	if data["has_more"]:
		return do_get_request_card_names_set(data["next_page"], all_reqest_card_names)
	else:
		return True


# CARDS NOT IN COLLECTION
# Compares the deck histogram with the collection histogram to determine which cards are needed in what quantities
def get_deck_upgrade(collection, decklist):
	print("Comparing decklist to collection to find cards needed to upgrade")
	upgrades = {}
	for name in decklist.keys():
		if name not in collection:
			upgrades[name] = decklist[name]
		else:
			if decklist[name] > collection[name]:
				upgrades[name] = decklist[name] - collection[name]
	# print(name)

	return upgrades


# CARDS THAT ARE IN COLLECTION
# Reverses the get_deck_upgrade() algorithm returning the number of cards that ARE in the given collection
def get_upgrades_in_collection(collection, decklist):
	print("Comparing decklist to collection to find cards that are already in collection.")
	upgrades = {}
	for name in decklist.keys():
		if name in collection:
			# If more cards are needed than exist in the collection, return number in collection
			if decklist[name] > collection[name]:
				upgrades[name] = collection[name]
			# If there are more cards in collection than cards needed, return cards needed
			else:
				upgrades[name] = decklist[name]
	# print(name)

	return upgrades


# Takes a dictionary and returns a list of card object-like dictionaries
def format_card_histogram(upgrades):
	all_upgrade_cards = []
	for name in upgrades.keys():
		new_line = {"name": name, "count": upgrades[name]}
		all_upgrade_cards.append(new_line)

	return all_upgrade_cards


# Ties the above three methods together
# Returns a list of dictionaries
def controller_get_upgrades(collection_path="audit_csv.csv", decklist_path="bin/decklist.txt"):
	all_cards = read_csv(name=collection_path, do_snake_case_names=True)
	collection = get_audit_card_histogram(all_cards)

	decklist = parse_text_decklist(read_txt(decklist_path))

	# write_data_dictionary(decklist, "decklist")

	upgrades = get_deck_upgrade(collection, decklist)
	print("Complete!")

	return format_card_histogram(upgrades)


# Ties the above three methods together
# Returns a list of dictionaries
def controller_get_decklist_upgrades_in_collection(collection_path="audit_csv.csv", decklist_path="bin/decklist.txt"):
	all_cards = read_csv(name=collection_path, do_snake_case_names=True)
	collection = get_audit_card_histogram(all_cards)

	decklist = parse_text_decklist(read_txt(decklist_path))

	# write_data_dictionary(decklist, "decklist")

	found_upgrades = get_upgrades_in_collection(collection, decklist)
	print("Complete!")

	return format_card_histogram(found_upgrades)


def controller_get_api_upgrades_in_collection(collection_path="audit_csv.csv", request_url=""):
	all_cards = read_csv(name=collection_path, do_snake_case_names=True)
	collection = get_audit_card_histogram(all_cards)

	decklist = get_decklist_from_api(request_url)

	# write_data_dictionary(decklist, "decklist")

	found_upgrades = get_upgrades_in_collection(collection, decklist)
	print(f"Complete! Found {len(found_upgrades)} cards!")

	return format_card_histogram(found_upgrades)


if __name__ == '__main__':
	print("Comparing decklist against collection")
	# all_upgrade_cards = controller_get_upgrades(decklist_path="bin/common_cube.txt", collection_path="audit_csv.csv")
	# all_upgrade_cards = controller_get_upgrades_in_collection(collection_path="all_audit_cards_new.csv",
	#                                                           decklist_path="bin/new_cards.txt")
	# print(all_upgrade_cards)
	# write_data(all_upgrade_cards)
	format = "commander"
	otag = "ramp"
	id = "gu"
	collection_path = "audit_csv.csv"
	# collection_path = "audit_csv_h.csv"
	request_url = f"https://api.scryfall.com/cards/search?q=otag%3A{otag}+id%3A{id}+f%3A{format}&unique=cards&as=grid"
	# request_url = "https://api.scryfall.com/cards/search?q=f%3Apauper+cmc%3A1+c%3Ag+type%3Acreature"
	all_upgrade_cards = controller_get_api_upgrades_in_collection(collection_path=collection_path,
	                                                              request_url=request_url)
	print(all_upgrade_cards)
	write_data(all_upgrade_cards)
