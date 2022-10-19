import random
from src.shared_methods_io import read_csv, write_data_dictionary
from enum import Enum, auto


class Card:
	name = ""
	card_class = ""
	wincon = 0
	combo_pieces = []

	def __init__(self, name="", card_class="", wincon=-1):
		self.name = name
		self.card_class = card_class
		self.wincon = wincon
		self.combo_pieces = []

	def __copy__(self):
		return Card(self.name, self.card_class, self.wincon)

	def string(self):
		return f"{self.name}: {self.card_class} {self.wincon}"

	def add_combo_pieces(self, combo_piece):
		self.combo_pieces.append(combo_piece)

	def clear_combo_pieces(self):
		self.combo_pieces.clear()


class Library:
	all_cards = []
	commander = Card()
	deck_name = ""

	def __init__(self, card=Card(), deck_name=""):
		self.all_cards = []
		self.commander = card
		self.deck_name = deck_name

	def __len__(self):
		return len(self.all_cards)

	def add_card(self, card):
		self.all_cards.append(card)

	def draw_card(self, hand, inactive_combo_pieces):
		this_card = self.all_cards.pop()
		for combo_pieces in this_card.combo_pieces:
			inactive_combo_pieces.append(combo_pieces)
		hand.append(this_card)

		return True

	def draw_commander(self, hand, inactive_combo_pieces):
		for combo_pieces in self.commander.combo_pieces:
			inactive_combo_pieces.append(combo_pieces)
		hand.append(self.commander)

		return True

	def set_commander(self, card):
		self.commander = card

	def shuffle(self):
		# self.all_cards.
		new_order = []
		while len(self.all_cards) > 0:
			i = random.randrange(len(self.all_cards))
			new_order.append(self.all_cards.pop(i))
		self.all_cards = new_order

	def print_all_cards(self):
		string = f"Total cards: {len(self.all_cards)}\n"
		for card in self.all_cards:
			string += card.string() + " | "
		return string

	def print(self):
		return f"{self.deck_name}, commander: {self.commander.name} | {len(self.all_cards)} cards"


class ComboPiece:
	name = ""
	is_payoff = False
	is_active = False
	requirements = set()
	results = set()

	def __init__(self, is_payoff=False, is_active=False, name=""):
		self.is_payoff = is_payoff
		self.is_active = is_active
		self.requirements = set()
		self.results = set()
		self.name = name


class ComboElements(Enum):
	INFINITE_UNTAP_LANDS = auto()
	INFINITE_UNTAP_CREATURE = auto()
	INFINITE_MANA = auto()
	INFINITE_ETB_CREATURE = auto()
	INFINITE_LANDFALL = auto()
	INF_RETURN_TO_HAND = auto()
	DOUBLE_ABILITIES = auto()
	HASTE = auto()
	CREATURES_ARE_LANDS = auto()
	LANDS_ARE_FORESTS = auto()
	BIG_MANA = auto()
	# Payoffs
	INFINITE_DAMAGE = auto()
	INFINITE_POWER = auto()
	INFINITE_DRAW = auto()
	WIN_THE_GAME = auto()


def import_cards_to_library(filename):
	all_cards = read_csv(filename)
	this_library = Library()
	for row in all_cards:
		new_card = Card(row['Name'], row['Class'], int(row['Wincon']))
		this_library.add_card(new_card)
	return this_library


def draw_wincon(library, pieces):
	library.shuffle()
	draws = 0
	hand = []
	wincons = []
	for i in range(pieces):
		wincons.append(i + 1)
	while len(wincons) > 0 and len(library) > 0:
		draws += 1
		hand.append(library.all_cards.pop())
		# print(hand[-1].string())
		if hand[-1].wincon in wincons:
			wincons.remove(hand[-1].wincon)

	for card in hand:
		library.add_card(card)

	if len(wincons) == 0:
		# print(f"Success! Win Con found in {draws} draws!")
		pass
	else:
		print("Error! Entire deck drawn but no win con was found!")
		draws = -1
	return draws


def big_simulate(n, library, pieces):
	all_draws = []
	for draw in range(n):
		i = draw_wincon(library, pieces)
		all_draws.append(i)
	# print(all_draws)
	return all_draws


def analyze_simulations(all_draws):
	histogram = {}
	for draw in all_draws:
		if draw in histogram:
			histogram[draw] += 1
		else:
			histogram[draw] = 1

	return histogram


# # # DRAW COMBOS # # #

def analyze_combos(hand, inactive_combo_pieces, all_active_elements):
	do = True
	while do:
		do = False
		for combo_piece in inactive_combo_pieces():
			for requirement in combo_piece.requirements:
				if requirement in all_active_elements:
					combo_piece.requirements.remove(requirement)

			# If piece is active, adds activated elements to list
			if combo_piece.is_active or len(combo_piece.requirements) == 0:
				for element in combo_piece.results:
					all_active_elements.add(element)
				inactive_combo_pieces.remove(combo_piece)
				do = True  # Resets do to loop again


def draw_combos(library):
	library.shuffle()
	draws = 0
	has_won = False
	hand = []
	inactive_combo_pieces = []
	all_active_elements = set()
	library.draw_commander(hand, inactive_combo_pieces)

	while len(library) > 0 and not has_won:
		library.draw_card(hand, inactive_combo_pieces)
		analyze_combos(hand, inactive_combo_pieces, all_active_elements)


def new_combo_test():
	this_library = Library()
	commander = Card("Ashaya", "Commander", 0)
	ashaya_combo = ComboPiece(False, True, "Ashaya creatures are lands")
	ashaya_combo.results.add(ComboElements.CREATURES_ARE_LANDS)
	commander.combo_pieces.append(ashaya_combo)

	ley_weaver = Card("Ley Weaver", "Untap", 1)
	ley_weaver_combo = ComboPiece(name="Ley Weaver Ashaya Mana")
	ley_weaver_combo.requirements.add(ComboElements.CREATURES_ARE_LANDS)
	ley_weaver_combo.results.add(ComboElements.INFINITE_UNTAP_CREATURE)
	ley_weaver_combo.results.add(ComboElements.INFINITE_UNTAP_LANDS)
	ley_weaver.combo_pieces.append(ley_weaver_combo)

	forest = Card("Forest", "Land", 0)
	forest_combo = ComboPiece(name="Forest Mana")
	forest_combo.requirements.add(ComboElements.INFINITE_UNTAP_LANDS)
	forest_combo.results.add(ComboElements.INFINITE_MANA)
	forest.combo_pieces.append(forest_combo)

	this_library.commander = commander
	this_library.add_card(ley_weaver)
	this_library.add_card(forest)
	draw_combos(this_library)


if __name__ == '__main__':
	print("Welcome to Magic Hands!")
	new_combo_test()
# library = import_cards_to_library("all_cards.csv")
# all_draws = big_simulate(1000, library, 2)
# histogram = analyze_simulations(all_draws)
# write_data_list(all_draws, "all")
# write_data_dictionary(histogram, "hist")
