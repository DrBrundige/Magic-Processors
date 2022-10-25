# Custom Scan methods examine a scryfall card and return either true or false.

# Checks if the card is eternal legal.
# Unfortunately, this is the only way to distinguish between Magic cards and tokens, art cards, and other stuff
def scan_card_is_eternal(scryfall_card):
	if 'legalities' in scryfall_card and scryfall_card['legalities']['vintage'] != 'not_legal':
		return True
	else:
		return False


# Scans all cards
def scan_is_card(scryfall_card):
	return True
