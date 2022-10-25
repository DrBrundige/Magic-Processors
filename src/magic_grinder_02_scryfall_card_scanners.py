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
