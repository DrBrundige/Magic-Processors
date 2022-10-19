from shared_methods_io import read_json
import os


# Deprecated. Imports Scryfall download file with the given name
def import_scryfall(path):
	print("Importing Scryfall data at " + path)
	return read_json(path)


# For a given type line, returns card base type
def get_card_type(type_line):
	if type_line.find("Token") > -1:
		return "Token"
	if type_line.find("Basic") > -1:
		return "Basic Land"
	if type_line.find("Land") > -1:
		return "Land"
	elif type_line.find("Creature") > -1:
		return "Creature"
	elif type_line.find("Artifact") > -1:
		return "Artifact"
	elif type_line.find("Enchantment") > -1:
		return "Enchantment"
	elif type_line.find("Instant") > -1:
		return "Instant"
	elif type_line.find("Sorcery") > -1:
		return "Sorcery"
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
def get_card_id_code(color_identity):
	num_colors = len(color_identity)
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

	return ""


# Returns a string representing the card variant - full art, frame effects, etc.
#    Normal cards are returned as (2015) Frame.
def get_card_variant(card):
	is_frame_effects_in_card = "frame_effects" in card
	is_finishes_in_card = "finishes" in card

	if card['full_art'] or (is_frame_effects_in_card and "fullart" in card["frame_effects"]):
		return "Full Art"
	elif card['border_color'] == "borderless":
		return "Borderless"
	elif is_frame_effects_in_card and "extendedart" in card["frame_effects"]:
		return "Extended Art"
	elif is_finishes_in_card and "etched" in card["finishes"]:
		return "Foil Etched"
	elif is_frame_effects_in_card and "showcase" in card["frame_effects"]:
		return "Showcase"
	else:
		return card["frame"] + " Frame"


# Returns a list containing each creature type according to the CR, last updated 2022-10-07
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


def prepare_cards_for_export(data):
	all_rows = []
	for key in data:
		this_row = data[key].copy()
		this_row["card_identifier"] = key

		all_rows.append(this_row)
	return all_rows


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


if __name__ == '__main__':
	print("Get card features")
# data = import_scryfall("some_cards.json")
# print("Data imported")

# for card in data:
# 	print(f"{card['name']} | {get_card_variant(card)}")
# print(get_oracle_text_without_reminder_text(
#     "Cumulative upkeep {1}{B} (At the beginning of your upkeep, put an age counter on this permanent, then sacrifice it unless you pay its upkeep cost for each age counter on it.) At the beginning of each upkeep, if Tombstone Stairwell is on the battlefield, each player creates a 2/2 black Zombie creature token with haste named Tombspawn for each creature card in their graveyard."))
