from shared_methods_grinder import *
from datetime import datetime, timedelta


# Outputs largely the same information plus price data
# name - input
# set - input
# set_num - input
# rarity - output
# foil - input
# variant - output
# price - output
# price_type - output
def get_card_usd(scryfall_card, card):
	new_line = {'name': card['name'], 'set': scryfall_card['set'].upper(),
	            'set_num': scryfall_card['collector_number'], 'rarity': scryfall_card['rarity'],
	            'foil': card['foil'], "variant": get_card_variant(scryfall_card)}

	all_prices = scryfall_card['prices']
	card_price = 0.0
	price_type = ""

	if new_line['variant'] == "Foil Etched" and 'usd_etched' in all_prices:
		card_price = all_prices['usd_etched']
		price_type = "usd_etched"
	elif card['foil'] == "1" and 'usd_foil' in all_prices:
		card_price = all_prices['usd_foil']
		price_type = "usd_foil"
	elif 'usd' in all_prices:
		card_price = all_prices['usd']
		price_type = "usd"

	new_line['price'] = card_price
	new_line['price_type'] = price_type

	return new_line


# Outputs rows for audit sheet. To wit:
# name - input
# id - empty
# set - input
# set_num - input
# is_foil - input
# variant - output
# spc - output
# home_box - empty
# location - empty
# section - empty
# box_code - empty
# year - output
# rarity - output
# card_type - output
# color_id - output
def get_audit_row(scryfall_card, card):
	# Creates a new Audit row from the matched card data
	new_line = {'name': card['name'], 'id': '', 'set': scryfall_card['set'].upper(),
	            'set_num': scryfall_card['collector_number'],
	            'is_foil': card['foil'], "variant": get_card_variant(scryfall_card)}

	# The spc column notes whether a card has a special collectible treatment.
	#    Cards with no such treatment are noted in the variant column as '2015 Frame'
	if "Frame" in new_line["variant"]:
		new_line["spc"] = 0
	else:
		new_line["spc"] = 1

	# These lines will be calculated once transferred to Excel
	new_line["home_box"] = ""
	new_line["location"] = ""
	new_line["section"] = ""
	new_line["box_code"] = ""

	# new_line["year"] = scryfall_card["released_at"][0:4]
	new_line["year"] = str(datetime.today().year)
	new_line["rarity"] = scryfall_card["rarity"][0].upper()
	new_line["card_type"] = get_card_type(scryfall_card["type_line"])
	new_line["color_id"] = get_card_id_code(scryfall_card["color_identity"])

	return new_line


# Outputs the information needed to bind to the full bulk data and create an audit row. To wit:
# name - input
# set - output
# set_num - output
# count - input
def get_input_row(scryfall_card, card):
	new_line = {'name': card['name'], 'set': scryfall_card['set'].upper(),
	            'set_num': scryfall_card['collector_number']}
	if 'count' in card:
		new_line['count'] = card['count']
	else:
		new_line['count'] = 1

	return new_line
