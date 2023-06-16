from shared_methods_io import read_csv, read_txt, write_data


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


# Compares the deck histogram with the collection histogram to determine which cards are needed in what quantities
def get_deck_upgrade(collection, decklist):
	print("Comparing decklist to collection")
	upgrades = {}
	for name in decklist.keys():
		if name not in collection:
			upgrades[name] = decklist[name]
		else:
			if decklist[name] > collection[name]:
				upgrades[name] = decklist[name] - collection[name]
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

	upgrades = get_deck_upgrade(collection, decklist)
	print("Complete!")

	return format_card_histogram(upgrades)


if __name__ == '__main__':
	print("Comparing decklist against collection")
	all_upgrade_cards = controller_get_upgrades()
	print(all_upgrade_cards)
	write_data(all_upgrade_cards)
