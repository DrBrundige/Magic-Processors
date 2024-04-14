from common_methods_io import read_json
import os
from unidecode import unidecode


# Deprecated. Use import_scryfall.import_scryfall_full() instead
# Imports Scryfall download file with the given name
def import_scryfall(path):
	print("Importing Scryfall data at " + path)
	return read_json(path)


# # # # # # # # # # # # #
# # #     LOGIC     # # #
# # # # # # # # # # # # #


# For a given type line, returns card base type. Prefers front face of card.
def get_card_type_from_type_line(type_line):
	is_double_faced = type_line.find(" // ")
	if is_double_faced > -1:
		type_line = type_line[0: is_double_faced]

	if type_line.find("Token") > -1:
		return "Token"
	elif type_line.find("Basic") > -1:
		return "Basic Land"
	elif type_line.find("Land") > -1:
		return "Land"
	elif type_line.find("Creature") > -1:
		if type_line.find("Artifact") > -1 or type_line.find("Vehicle") > -1:
			return "Artifact Creature"
		if type_line.find("Enchantment") > -1:
			return "Enchantment Creature"
		else:
			return "Creature"
	elif type_line.find("Artifact") > -1:
		if type_line.find("Equipment") > -1:
			return "Artifact Equipment"
		else:
			return "Artifact"
	elif type_line.find("Enchantment") > -1:
		return "Enchantment"
	elif type_line.find("Instant") > -1:
		return "Instant"
	elif type_line.find("Sorcery") > -1:
		return "Sorcery"
	elif type_line.find("Battle") > -1:
		return "Battle"
	elif type_line.find("Planeswalker") > -1:
		return "Planeswalker"
	else:
		i = type_line.find("—")
		if i < 0:
			return type_line
		else:
			return type_line[0:i - 1]


# A string of logic to return the formatted color combination for a list of colors
# Accepts a list of colors
# Returns the color combination as a string. On failure returns an empty string
def get_color_code_from_colors(color_identity):
	try:
		# Cards such as filter lands can technically produce six colors: WUBRG and C.
		# For this purpose, however either a card can produce only produce C or it can produce colored mana -
		# that it can do both is just not important and makes things more complicated. It is removed here.
		if "C" in color_identity:
			color_identity.remove("C")

		num_colors = len(color_identity)
		# Uses a long string of logic to determine color combination
		if num_colors == 0:
			return "C"
		elif num_colors == 1:
			return color_identity[0]
		elif num_colors == 2:
			if "W" in color_identity:
				if "U" in color_identity:
					return "WU"
				elif "B" in color_identity:
					return "WB"
				elif "R" in color_identity:
					return "RW"
				else:
					return "GW"

			elif "U" in color_identity:
				if "B" in color_identity:
					return "UB"
				elif "R" in color_identity:
					return "UR"
				else:
					return "GU"

			elif "B" in color_identity:
				if "R" in color_identity:
					return "BR"
				else:
					return "BG"

			elif "R" in color_identity:
				return "RG"

		elif num_colors == 3:
			if "W" in color_identity:
				if "U" in color_identity:
					if "B" in color_identity:
						return "WUB"
					elif "R" in color_identity:
						return "URW"
					else:
						return "GWU"
				elif "B" in color_identity:
					if "R" in color_identity:
						return "RWB"
					else:
						return "WBG"
				else:
					return "RGW"
			elif "U" in color_identity:
				if "B" in color_identity:
					if "R" in color_identity:
						return "UBR"
					else:
						return "BGU"
				else:
					return "GUR"
			else:
				return "BRG"

		elif num_colors == 4:
			if "W" not in color_identity:
				return "UBRG"
			elif "U" not in color_identity:
				return "BRGW"
			elif "B" not in color_identity:
				return "RGWU"
			elif "R" not in color_identity:
				return "GWUB"
			else:
				return "WUBR"

		elif num_colors >= 5:
			return "WUBRG"

		# If num_colors is <0 or >5, some bug has occurred. Returns empty string
		return ""
	except Exception as E:
		print("Errant operation parsing color ID")
		print(E)
		return ""


# Returns a string representing the card variant - full art, frame effects, etc.
#    Normal cards are returned as (2015) Frame.
def get_card_variant(scryfall_card):
	is_frame_effects_in_card = "frame_effects" in scryfall_card
	is_finishes_in_card = "finishes" in scryfall_card

	if scryfall_card['full_art'] or (is_frame_effects_in_card and "fullart" in scryfall_card["frame_effects"]):
		return "Full Art"
	elif scryfall_card['border_color'] == "borderless":
		return "Borderless"
	elif is_frame_effects_in_card and "extendedart" in scryfall_card["frame_effects"]:
		return "Extended Art"
	elif is_finishes_in_card and "etched" in scryfall_card["finishes"] and len(scryfall_card["finishes"]) == 1:
		return "Foil Etched"
	elif is_frame_effects_in_card and "showcase" in scryfall_card["frame_effects"]:
		return "Showcase"
	elif is_frame_effects_in_card and "inverted" in scryfall_card["frame_effects"]:
		return "Inverted"
	else:
		return scryfall_card["frame"] + " Frame"


# I would love to find a way to easily determine whether a card is a real card that can be added to a standard
#     Magic deck or some other item such as a token or art card. However, it seems no such logic exists -
#    indeed, the definition is highly malleable.
#    This method doesn't allow previewed cards that will become eternal once released, but it's close enough.
#    In any case, probably better to be too exclusive
# Accepts a scryfall_card object. Returns a bool
def get_card_is_eternal(scryfall_card):
	if "legalities" not in scryfall_card:
		return False
	else:
		return scryfall_card["legalities"]["vintage"] != "not_legal"


# # # # # # # # # # # # #
# # #     DATA      # # #
# # # # # # # # # # # # #

# Returns a list containing each creature type according to the CR, last updated 2022-10-07
# There's a Scryfall API endpoint that does this, but this is funnier
def get_all_creature_types():
	return ["Advisor", "Aetherborn", "Alien", "Ally", "Angel", "Antelope", "Ape", "Archer", "Archon", "Army",
	        "Artificer", "Assassin", "Assembly-Worker", "Astartes", "Atog", "Aurochs", "Avatar", "Azra", "Badger",
	        "Balloon", "Barbarian", "Bard", "Basilisk", "Bat", "Bear", "Beast", "Beeble", "Beholder", "Berserker",
	        "Bird", "Blinkmoth", "Boar", "Bringer", "Brushwagg", "Camarid", "Camel", "Caribou", "Carrier", "Cat",
	        "Centaur", "Cephalid", "Child", "Chimera", "Citizen", "Cleric", "Clown", "Cockatrice", "Construct",
	        "Coward", "Crab", "Crocodile", "C/'tan", "Custodes", "Cyclops", "Dauthi", "Demigod", "Demon", "Deserter",
	        "Devil", "Dinosaur", "Djinn", "Dog", "Dragon", "Drake", "Dreadnought", "Drone", "Druid", "Dryad", "Dwarf",
	        "Efreet", "Egg", "Elder", "Eldrazi", "Elemental", "Elephant", "Elf", "Elk", "Employee", "Eye", "Faerie",
	        "Ferret", "Fish", "Flagbearer", "Fox", "Fractal", "Frog", "Fungus", "Gamer", "Gargoyle", "Germ", "Giant",
	        "Gith", "Gnoll", "Gnome", "Goat", "Goblin", "God", "Golem", "Gorgon", "Graveborn", "Gremlin", "Griffin",
	        "Guest", "Hag", "Halfling", "Hamster", "Harpy", "Hellion", "Hippo", "Hippogriff", "Homarid", "Homunculus",
	        "Horror", "Horse", "Human", "Hydra", "Hyena", "Illusion", "Imp", "Incarnation", "Inkling", "Inquisitor",
	        "Insect", "Jackal", "Jellyfish", "Juggernaut", "Kavu", "Kirin", "Kithkin", "Knight", "Kobold", "Kor",
	        "Kraken", "Lamia", "Lammasu", "Leech", "Leviathan", "Lhurgoyf", "Licid", "Lizard", "Manticore", "Masticore",
	        "Mercenary", "Merfolk", "Metathran", "Minion", "Minotaur", "Mole", "Monger", "Mongoose", "Monk", "Monkey",
	        "Moonfolk", "Mouse", "Mutant", "Myr", "Mystic", "Naga", "Nautilus", "Necron", "Nephilim", "Nightmare",
	        "Nightstalker", "Ninja", "Noble", "Noggle", "Nomad", "Nymph", "Octopus", "Ogre", "Ooze", "Orb", "Orc",
	        "Orgg", "Otter", "Ouphe", "Ox", "Oyster", "Pangolin", "Peasant", "Pegasus", "Pentavite", "Performer",
	        "Pest", "Phelddagrif", "Phoenix", "Phyrexian", "Pilot", "Pincher", "Pirate", "Plant", "Praetor", "Primarch",
	        "Prism", "Processor", "Rabbit", "Raccoon", "Ranger", "Rat", "Rebel", "Reflection", "Rhino", "Rigger",
	        "Robot", "Rogue", "Sable", "Salamander", "Samurai", "Sand", "Saproling", "Satyr", "Scarecrow", "Scion",
	        "Scorpion", "Scout", "Sculpture", "Serf", "Serpent", "Servo", "Shade", "Shaman", "Shapeshifter", "Shark",
	        "Sheep", "Siren", "Skeleton", "Slith", "Sliver", "Slug", "Snake", "Soldier", "Soltari", "Spawn", "Specter",
	        "Spellshaper", "Sphinx", "Spider", "Spike", "Spirit", "Splinter", "Sponge", "Squid", "Squirrel", "Starfish",
	        "Surrakar", "Survivor", "Tentacle", "Tetravite", "Thalakos", "Thopter", "Thrull", "Tiefling", "Treefolk",
	        "Trilobite", "Triskelavite", "Troll", "Turtle", "Tyranid", "Unicorn", "Vampire", "Vedalken", "Viashino",
	        "Volver", "Wall", "Walrus", "Warlock", "Warrior", "Weird", "Werewolf", "Whale", "Wizard", "Wolf",
	        "Wolverine", "Wombat", "Worm", "Wraith", "Wurm", "Yeti", "Zombie", "Zubera"]


# Checks to see if a field in a given card. If not, checks the front face for that field
# Multifaced cards have some fields in the face object
def get_field_from_card(field, scryfall_card, not_found=""):
	if field in scryfall_card:
		return scryfall_card[field]
	else:
		if "card_faces" in scryfall_card and field in scryfall_card["card_faces"][0]:
			return scryfall_card["card_faces"][0][field]
		else:
			return not_found


def get_usd_from_card(card, scryfall_card, output_price_type=False):
	try:
		all_prices = scryfall_card["prices"]
		card_price = "0.0"
		price_type = ""
		# Re-calculating the card variant here is less efficient
		#    but makes the method more self-contained and robust
		variant = get_card_variant(scryfall_card)
		is_foil_only = scryfall_card["foil"] and not scryfall_card["nonfoil"]
		card_is_foil = 'foil' in card and card['foil'] == "1"

		if variant == "Foil Etched" and 'usd_etched' in all_prices \
				and all_prices['usd_etched'] is not None:
			card_price = all_prices['usd_etched']
			price_type = "usd_etched"
		elif ((card_is_foil or is_foil_only) and 'usd_foil' in all_prices) \
				and all_prices['usd_foil'] is not None:
			card_price = all_prices['usd_foil']
			price_type = "usd_foil"
		elif 'usd' in all_prices and all_prices['usd'] is not None:
			card_price = all_prices['usd']
			price_type = "usd"

		card['value'] = card_price
		if output_price_type:
			card['price_type'] = price_type

		return True
	except Exception as E:
		print("Errant operation calculating price")
		print(E)
		return False


# Handles the verbose logic to assign a card a default section for the audit sheet
#    As of the 2023 Audit, this information can be derived entirely from the card itself
# Returns a string
def assign_default_section(scryfall_card):
	try:
		# Logic for basic lands
		card_type = get_card_type_from_type_line(scryfall_card["type_line"])
		# if card_type == "Basic Land":
		# 	# Maybe someday I can make a section for snow lands. IDK
		# 	# Retrieves color ID. Normally I like to sort by color rather than ID,
		# 	#    but since lands are colorless it's a bit easier to do it this way
		# 	id = get_color_code_from_colors(scryfall_card["color_identity"])
		# 	if id == "W":
		# 		return "201 - White"
		# 	elif id == "U":
		# 		return "202 - Blue"
		# 	elif id == "B":
		# 		return "203 - Black"
		# 	elif id == "R":
		# 		return "204 - Red"
		# 	elif id == "G":
		# 		return "205 - Green"
		# 	else:
		# 		return "501 - Land (Basic)"

		# Most cards are sorted by color with some special rules for lands and artifacts
		color = get_color_code_from_colors(get_field_from_card("colors", scryfall_card))

		produced_mana = get_field_from_card("produced_mana", scryfall_card, not_found="none")
		if produced_mana != "none":
			produced_mana = get_color_code_from_colors(produced_mana)
		else:
			produced_mana = ""

		if color != "C":
			if len(color) > 1:
				# If the length of the card's color is greater than one, then it is multicolor
				return "31 - Multicolor"
			elif color == "W":
				return "21 - White"
			elif color == "U":
				return "22 - Blue"
			elif color == "B":
				return "23 - Black"
			elif color == "R":
				return "24 - Red"
			elif color == "G":
				return "25 - Green"
		elif "Artifact" in card_type:
			if card_type == "Artifact Creature":
				return "41 - Artifact (Artifact Creature)"
			elif card_type == "Artifact Equipment":
				return "44 - Artifact (Equipment)"
			elif len(produced_mana) > 0:
				return "43 - Artifact (Mana Rock)"
			else:
				return "42 - Artifact (Utility Artifact)"
		elif "Land" in card_type:
			if card_type == "Basic Land":
				return "51 - Land (Basic)"
			elif len(produced_mana) > 1:
				return "52 - Lands (Color Fixing)"
			else:
				return "53 - Lands (Utility Lands)"
		else:
			return "11 - Colorless"
	except Exception as E:
		print("Errant operation assigning default section!")
		print(E)
		return ""


# Gets the price range for the given card
def assign_price_range(card, high_value=2):
	try:
		if float(card["value"]) > high_value:
			return "01 - Rares"
		elif card["rarity"] == "R" or card["rarity"] == "M":
			return "02 - Bulk Rares"
		else:
			return "03 - Bulk Commons"
	except ValueError as V:
		print("Value error calculating price range. Blanking card['value']")
		card["value"] = "0"
		return assign_price_range(card, high_value)


# # # # # # # # # # # # # # # #
# # #     MANIPULATION    # # #
# # # # # # # # # # # # # # # #


# Converts a list of dictionaries into a list of lists with the dictionary keys in the first row.
#   I'm not sure whether it works
def prepare_cards_for_export(data):
	all_rows = []
	for key in data:
		this_row = data[key].copy()
		this_row["card_identifier"] = key

		all_rows.append(this_row)
	return all_rows


# Manually goes through each dictionary in a list to make sure the key value pairs are just how I like them
#     There's probably a more efficient way of doing this but I'm not sure what it is.
def format_cards_for_audit_sheet(data):
	try:
		headers = read_json("bin/audit_headers.json")
		for i in range(len(data)):
			this_card = data[i]
			new_card = {}
			for header in headers:
				if header in this_card:
					new_card[header] = this_card[header]
				else:
					new_card[header] = ""
			data[i] = new_card
	except Exception as E:
		print("Errant operation formatting cards!")
		print(E)
	return True


# A simple script to return a string removing any text between parentheses
def get_oracle_text_without_reminder_text(oracle_text):
	new_text = ""
	in_reminder = False

	for char in oracle_text:
		if not in_reminder:
			if char == "(":
				in_reminder = True
			else:
				new_text += char
		elif char == ")":
			in_reminder = False

	return new_text.strip()


# Clears special characters from a card name, capitalizes, and removes any back face
def scrub_card_name(card_name):
	card_name = unidecode(card_name).upper()
	# Strips special characters from card name

	if "//" in card_name:
		card_name = card_name[0:card_name.find("//")]

	new_card_name = ""
	for character in card_name:
		if 65 <= ord(character) <= 90:
			new_card_name += character

	return new_card_name


if __name__ == '__main__':
	data = []
	format_cards_for_audit_sheet(data)
	print("Scrubbing card names")
	print(scrub_card_name("Colossal Badger // Dig Deeper"))
	print(scrub_card_name("Tocasia's Dig Site "))

# data = import_scryfall("some_cards.json")
# print("Data imported")

# for card in data:
# 	print(f"{card['name']} | {get_card_variant(card)}")
# print(get_oracle_text_without_reminder_text(
#     "Cumulative upkeep {1}{B} (At the beginning of your upkeep, put an age counter on this permanent, then sacrifice it unless you pay its upkeep cost for each age counter on it.) At the beginning of each upkeep, if Tombstone Stairwell is on the battlefield, each player creates a 2/2 black Zombie creature token with haste named Tombspawn for each creature card in their graveyard."))
