from common_methods_processor import get_card_variant


def get_usd_from_card_03(card, scryfall_card):
	try:
		all_prices = scryfall_card["prices"]
		card_price = "0.0"

		# Re-calculating the card variant here is less efficient
		#    but makes the method more self-contained and robust
		variant = get_card_variant(scryfall_card)

		is_foil_only = scryfall_card["foil"] and not scryfall_card["nonfoil"]
		card_is_foil = card.foil

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

		return card_price
	except Exception as E:
		print("Errant operation calculating price")
		print(E)
		return f"Error|{E}"


def get_cheapest_usd_from_scryfall_card(scryfall_card):
	try:
		all_prices = scryfall_card["prices"]
		usd_values = []

		if all_prices["usd"] is not None:
			usd_values.append(float(all_prices["usd"]))
		if all_prices["usd_foil"] is not None:
			usd_values.append(float(all_prices["usd_foil"]))
		if all_prices["usd_etched"] is not None:
			usd_values.append(float(all_prices["usd_etched"]))

		if len(usd_values) > 0:
			usd_values.sort()

			return usd_values[0]
		else:
			return False
	except Exception as E:
		print("Errant operation calculating price")
		print(E)
		return False


# I agonized over how to tell if a card was legal for constructed or not,
#   eventually deciding on checking the format legality. But guess what!
#   The gold border cards are marked as vintage legal too! Aaaaigh! Checks format and set type
# Accepts a scryfall_card object. Returns a bool
def get_card_is_constructed_legal(scryfall_card):
	if "legalities" not in scryfall_card or "set_type" not in scryfall_card:
		return False
	else:
		is_vintage_legal = scryfall_card["legalities"]["vintage"] != "not_legal"
		is_not_extra = scryfall_card["set_type"] != "memorabilia" and scryfall_card["set_type"] != "token"
		return is_vintage_legal and is_not_extra


# Gets the price range for the given card
def get_price_range_03(value, rarity, high_value=2):
	if float(value) > high_value:
		return "01 - Rares"
	elif rarity == "R" or rarity == "M":
		return "02 - Bulk Rares"
	else:
		return "03 - Bulk Commons"


# Returns a list containing each legal creature type according to the CR, last updated for MH3 2024-06-07
# Just found out that the Scryfall endpoint returns different data
def get_all_creature_types():
	return ["Advisor", "Aetherborn", "Alien", "Ally", "Angel", "Antelope", "Ape", "Archer", "Archon", "Armadillo",
	        "Army", "Artificer", "Assassin", "Assembly-Worker", "Astartes", "Atog", "Aurochs", "Avatar", "Azra",
	        "Badger", "Balloon", "Barbarian", "Bard", "Basilisk", "Bat", "Bear", "Beast", "Beaver", "Beeble",
	        "Beholder", "Berserker", "Bird", "Blinkmoth", "Boar", "Bringer", "Brushwagg", "Camarid", "Camel",
	        "Capybara", "Caribou", "Carrier", "Cat", "Centaur", "Child", "Chimera", "Citizen", "Cleric", "Clown",
	        "Cockatrice", "Construct", "Coward", "Coyote", "Crab", "Crocodile", "C’tan", "Custodes", "Cyberman",
	        "Cyclops", "Dalek", "Dauthi", "Demigod", "Demon", "Deserter", "Detective", "Devil", "Dinosaur", "Djinn",
	        "Doctor", "Dog", "Dragon", "Drake", "Dreadnought", "Drone", "Druid", "Dryad", "Dwarf", "Efreet", "Egg",
	        "Elder", "Eldrazi", "Elemental", "Elephant", "Elf", "Elk", "Employee", "Eye", "Faerie", "Ferret", "Fish",
	        "Flagbearer", "Fox", "Fractal", "Frog", "Fungus", "Gamer", "Gargoyle", "Germ", "Giant", "Gith", "Gnoll",
	        "Gnome", "Goat", "Goblin", "God", "Golem", "Gorgon", "Graveborn", "Gremlin", "Griffin", "Guest", "Hag",
	        "Halfling", "Hamster", "Harpy", "Hellion", "Hippo", "Hippogriff", "Homarid", "Homunculus", "Horror",
	        "Horse", "Human", "Hydra", "Hyena", "Illusion", "Imp", "Incarnation", "Inkling", "Inquisitor", "Insect",
	        "Jackal", "Jellyfish", "Juggernaut", "Kavu", "Kirin", "Kithkin", "Knight", "Kobold", "Kor", "Kraken",
	        "Llama", "Lamia", "Lammasu", "Leech", "Leviathan", "Lhurgoyf", "Licid", "Lizard", "Manticore", "Masticore",
	        "Mercenary", "Merfolk", "Metathran", "Minion", "Minotaur", "Mite", "Mole", "Monger", "Mongoose", "Monk",
	        "Monkey", "Moonfolk", "Mount", "Mouse", "Mutant", "Myr", "Mystic", "Nautilus", "Necron", "Nephilim",
	        "Nightmare", "Nightstalker", "Ninja", "Noble", "Noggle", "Nomad", "Nymph", "Octopus", "Ogre", "Ooze", "Orb",
	        "Orc", "Orgg", "Otter", "Ouphe", "Ox", "Oyster", "Pangolin", "Peasant", "Pegasus", "Pentavite", "Performer",
	        "Pest", "Phelddagrif", "Phoenix", "Phyrexian", "Pilot", "Pincher", "Pirate", "Plant", "Porcupine", "Possum",
	        "Praetor", "Primarch", "Prism", "Processor", "Rabbit", "Raccoon", "Ranger", "Rat", "Rebel", "Reflection",
	        "Rhino", "Rigger", "Robot", "Rogue", "Sable", "Salamander", "Samurai", "Sand", "Saproling", "Satyr",
	        "Scarecrow", "Scientist", "Scion", "Scorpion", "Scout", "Sculpture", "Serf", "Serpent", "Servo", "Shade",
	        "Shaman", "Shapeshifter", "Shark", "Sheep", "Siren", "Skeleton", "Slith", "Sliver", "Sloth", "Slug",
	        "Snail", "Snake", "Soldier", "Soltari", "Spawn", "Specter", "Spellshaper", "Sphinx", "Spider", "Spike",
	        "Spirit", "Splinter", "Sponge", "Squid", "Squirrel", "Starfish", "Surrakar", "Survivor", "Synth",
	        "Tentacle", "Tetravite", "Thalakos", "Thopter", "Thrull", "Tiefling", "Treefolk", "Trilobite",
	        "Triskelavite", "Troll", "Turtle", "Tyranid", "Unicorn", "Vampire", "Varmint", "Vedalken", "Volver", "Wall",
	        "Walrus", "Warlock", "Warrior", "Weird", "Werewolf", "Whale", "Wizard", "Wolf", "Wolverine", "Wombat",
	        "Worm", "Wraith", "Wurm", "Yeti", "Zombie", "Zubera", "Time Lord"]


def sort_cards_by_set_num(all_cards):
	sorted_cards = []
	sorted_nums_ints = []
	sorted_keys_strs = []

	for card in all_cards:
		# in_card = 'collect_number' in card
		# num_is_digit = card["collector_number"].isdigit()
		# num = card["collector_number"]
		if card["collector_number"].isdigit():
			sorted_nums_ints.append(card)
		else:
			sorted_keys_strs.append(card)

	sorted_nums_ints.sort(key=sort_set_num_int)
	sorted_keys_strs.sort(key=sort_set_num_str)

	for sorted_int in sorted_nums_ints:
		sorted_cards.append(sorted_int)

	for sorted_str in sorted_keys_strs:
		sorted_cards.append(sorted_str)

	return sorted_cards


def sort_set_num_str(card):
	# if "collect_number" in card:
	return card["collector_number"]


# else:
# 	return ""


def sort_set_num_int(card):
	# if "collect_number" in card.keys():
	return int(card["collector_number"])


# else:
# 	return 0

# Returns true if the card is in an expansion or core set released on or after Return to Ravnica
def card_is_pioneer_legal_set(scryfall_card):
	is_expansion_or_core = "set_type" in scryfall_card and (
			scryfall_card["set_type"] == "expansion" or scryfall_card["set_type"] == "core")
	is_after_rtr = "released_at" in scryfall_card and scryfall_card["released_at"] >= "2012-10-05"
	return is_after_rtr and is_expansion_or_core


# Despite my efforts, I have not been able to identify an API or some such to return the current standard sets.
# So this will have to be hard-coded.
def card_is_standard_legal_set(scryfall_card):
	standard_sets = ["dmu", "bro", "one", "mom", "mat", "woe", "lci", "mkm", "otj", "blb", "dsk"]
	return "set" in scryfall_card and scryfall_card["set"] in standard_sets
