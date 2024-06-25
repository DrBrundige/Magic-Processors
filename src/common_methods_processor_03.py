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
