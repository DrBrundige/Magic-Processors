# Custom Scan methods examine a scryfall card and return either true or false.

# Checks if the card is eternal legal.
# Unfortunately, this is the only way to distinguish between Magic cards and tokens, art cards, and other stuff
def scan_card_is_eternal(scryfall_card):
	if 'legalities' in scryfall_card and scryfall_card['legalities']['vintage'] != 'not_legal':
		return True
	else:
		return False


def scan_card_eternal_set(scryfall_card):
	legal_set_types = {'core', 'expansion', 'duel_deck', 'funny', 'masterpiece', 'commander', 'draft_innovation',
	                   'starter', 'arsenal', 'box', 'masters', 'archenemy', 'planechase'}
	if 'set_type' in scryfall_card and scryfall_card['set_type'] in legal_set_types:
		return True
	else:
		return False


# Checks if the card is printed in pager
# Unfortunately, this is the only way to distinguish between Magic cards and tokens, art cards, and other stuff
def scan_card_is_paper(scryfall_card):
	if 'games' in scryfall_card and 'paper' in scryfall_card['games']:
		return True
	else:
		return False


# Scans all cards
def scan_is_card(scryfall_card):
	return True
