
import random

# from cool_stuff import clean_word, write_data_list


# Simulates a magic draw with replacement.
#   Finds the total number of economic cards you are likely to draw for a given ratio
def simple_simulate_hands(n=1000, lands=55, total=99):
	all_draws = []
	draws_histogram = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}

	for s in range(n):
		lands_in_deck = lands
		other_in_deck = total - lands
		lands_in_hand = 0
		draws = 0
		go = True
		while draws < 7 and go:
			this_draw = random.randrange(0, lands_in_deck + other_in_deck)
			if this_draw > lands_in_deck:
				# print("Drew a land card!")
				lands_in_hand += 1
				lands_in_deck -= 1
			else:
				# print("Did not draw a land card!")
				other_in_deck -= 1

			draws += 1

			if lands_in_deck == 0:
				go = False
			# print("There are no more land cards in the deck!")
			if other_in_deck == 0:
				go = False
		# print("There are only land cards in the deck!")
		# print(f"\tTotal lands drawn: {lands_in_hand}")
		all_draws.append(lands_in_hand)
		draws_histogram[lands_in_hand] = draws_histogram[lands_in_hand] + 1
	print(f"Success! Simulated {n} draws!")
	return draws_histogram


# Simulates drawing from deck until a win condition card is found
def draw_win_condition(n=1000, wins=4, total=99):
	# This stores for our simulations
	all_draws = []

	for s in range(n):
		# Deck is simulated as integers representing win cards and all other cards
		other_in_deck = total - wins
		draws = 0
		# This bool is set to false once a win card is drawn
		go = True

		while go and draws < total:
			# Every iteration, a random integer is picked.
			#   If it is less than the number of win cards, a win is drawn
			this_draw = random.randrange(0, other_in_deck)
			if this_draw < wins:
				# print("Drew a win card!")
				go = False
			else:
				# print("Did not draw a win card!")
				# Another card is drawn. Deincrement the number of cards by one
				other_in_deck -= 1
			draws += 1
		all_draws.append(draws)

	return all_draws
