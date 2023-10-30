from shared_methods_grinder import *
from datetime import datetime, timedelta

# TODO: Change these to update a parameterized card object and return True / False

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
	try:
		is_foil = card['foil']
		card = {'': ''}
		card = {'name': scryfall_card['name'], 'set': scryfall_card['set'].upper(),
		        'set_num': scryfall_card['collector_number'], 'rarity': scryfall_card['rarity'],
		        'foil': is_foil, "variant": get_card_variant(scryfall_card)}

		get_usd_from_card(card, scryfall_card, output_price_type=True)
		# card = new_line
		return True
	except Exception as E:
		print("Errant operation processing card value")
		print(E)
		return False


# Outputs rows for audit sheet. To wit:
# name -     input
# id -       empty
# set -      input
# set_num -  input
# is_foil -  input
# variant -  output
# spc -      output
# home_box - empty
# location - empty
# section -  empty
# year -     output
# rarity -   output
# card_type -output
# color_id - output
# colors -   output
def get_audit_row(scryfall_card, card):
	# Creates a new Audit row from the matched card data
	card['name'] = scryfall_card['name']
	if 'id' in card:
		card['id'] = card['id']
	else:
		card['id'] = ''
	card['set'] = scryfall_card['set'].upper()

	card['collector_number'] = scryfall_card['collector_number']
	card['foil'] = card['foil']

	card['variant'] = get_card_variant(scryfall_card)

	# The spc column notes whether a card has a special collectible treatment.
	#    Cards with no such treatment are noted in the variant column as '2015 Frame'
	if "Frame" in card["variant"]:
		card["spc"] = "0"
	else:
		card["spc"] = "1"

	# These lines will be calculated once transferred to Excel
	if "home_box" not in card:
		card["home_box"] = ""
	# card["location"] = ""
	card["price_range"] = ""
	card["section"] = assign_default_section(scryfall_card)

	# new_line["year"] = scryfall_card["released_at"][0:4]
	if "year" not in card:
		card["year"] = str(datetime.today().year)
	card["input_code"] = f"{card['name']} ({card['set']}) {card['collector_number']}"

	card["rarity"] = scryfall_card["rarity"][0].upper()
	card["card_type"] = get_card_type_from_type_line(scryfall_card["type_line"])
	card["colors"] = get_color_code_from_colors(get_field_from_card("colors", scryfall_card))
	card["color_id"] = get_color_code_from_colors(scryfall_card["color_identity"])

	produced_mana = get_field_from_card("produced_mana", scryfall_card, not_found="none")

	if produced_mana != "none":
		card["produced_mana"] = get_color_code_from_colors(produced_mana)
	else:
		card["produced_mana"] = ""

	card["code"] = f"{scryfall_card['set'].upper()}|{scryfall_card['collector_number']}"

	get_usd_from_card(card, scryfall_card, output_price_type=False)

	# if "edhrec_rank" in scryfall_card:
	# 	card["edhrec_rank"] = scryfall_card["edhrec_rank"]
	# else:
	# 	card["edhrec_rank"] = "99999999"

	if "released_at" in scryfall_card:
		card["released_at"] = scryfall_card["released_at"]
	else:
		card["released_at"] = ""

	# The "price_range" field is declared in the middle of the object
	#    but not calculated until the end. This extremely bootleg solution makes sure
	#    the assign_price_range() method has all the information it needs while ensuring the column
	#    is in the order I like it
	card["price_range"] = assign_price_range(card, 2)

	return True


# Outputs the information needed to bind to the full bulk data and create an audit row. To wit:
# name - input
# set - output
# set_num - output
# count - input
def get_input_row(scryfall_card, card):
	new_line = {'name': scryfall_card['name'], 'set': scryfall_card['set'].upper(),
	            'set_num': scryfall_card['collector_number']}
	if 'count' in card:
		new_line['count'] = card['count']
	else:
		new_line['count'] = 1

	return new_line


# Outputs the information I like to have on my printed card wishlist. Note: I am insane. To wit:
# name - input
# set - output
# set_num - output
# rarity - output
# color - output
def get_wishlist_row(scryfall_card, card):
	try:
		card['name'] = scryfall_card['name']
		card['set'] = scryfall_card['set'].upper()
		card['set_num'] = scryfall_card['collector_number']
		card['rarity'] = scryfall_card['rarity'][0].upper()
		card['color'] = get_color_code_from_colors(scryfall_card['color_identity'])

		return True
	except Exception as E:
		print("Errant operation preparing wishlist row!")
		print(E)
		return False

# Outputs the information that I like to have for set sheets. To wit:
# name - output
# count - blank
# foil - blank
# collector_number - output
# rarity - output
# artist - output
# value - output
# variant - output
def get_set_sheet(scryfall_card, card):
	try:
		card['name'] = scryfall_card['name']
		card['count'] = ""
		card['foil'] = ""
		card['collector_number'] = scryfall_card['collector_number']
		card['rarity'] = scryfall_card["rarity"][0].upper()
		if "type_line" in scryfall_card:
			card["card_type"] = get_card_type_from_type_line(scryfall_card["type_line"])
		else:
			card["card_type"] = ""
		card["colors"] = get_color_code_from_colors(get_field_from_card("colors", scryfall_card))
		card['artist'] = scryfall_card['artist']
		card['booster'] = scryfall_card['booster']
		card['variant'] = get_card_variant(scryfall_card)
		get_usd_from_card(card, scryfall_card, output_price_type=False)
		return True
	except Exception as E:
		print("Errant operation preparing set sheet row!")
		print(E)
		return False


# Outputs basic card information plus the URI to return the highest resolution scan available
# name - output
# set - output
# collector_number - output
# image_uri - output
# resolution - output (output as name of file in scryfall object)
def get_card_images(scryfall_card, card):
	try:
		card['name'] = scryfall_card['name']
		card['set'] = scryfall_card['set']
		card['collector_number'] = scryfall_card['collector_number']

		if "image_uris" in scryfall_card:
			if "large" in scryfall_card["image_uris"]:
				card['image_uri'] = scryfall_card["image_uris"]["large"]
				card['resolution'] = "large"
			elif "normal" in scryfall_card["image_uris"]:
				card['image_uri'] = scryfall_card["image_uris"]["normal"]
				card['resolution'] = "normal"
			elif "small" in scryfall_card["image_uris"]:
				card['image_uri'] = scryfall_card["image_uris"]["small"]
				card['resolution'] = "small"
				# Somehow this card has neither small, medium, nor large image. We're done here.
			else:
				return False

		return True
	except Exception as E:
		print("Errant operation preparing card images!")
		print(E)
		return False


def get_cardname_data(scryfall_card, card):
	new_line = {'name': scryfall_card['name']}
	card = new_line

	return True
