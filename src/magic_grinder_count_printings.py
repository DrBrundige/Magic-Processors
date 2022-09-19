from magic_grinder import import_scryfall, get_card_type
from magic_grinder_common_printings import prepare_cards_for_export
import cool_stuff, count_condition


def count_printings(data, format="vintage", printing_conditions=None):
	if printing_conditions is None:
		printing_conditions = []
	found_cards = {}
	for card in data:
		if card['legalities'][format] != 'not_legal':
			conditions_met = True
			for condition in printing_conditions:
				# if card[condition['key']] != condition['value']:
				if not condition.check(card):
					conditions_met = False
			if conditions_met:
				name = card['name']
				if name in found_cards:
					found_cards[name] = found_cards[name] + 1
				else:
					found_cards[name] = 1

	return found_cards


if __name__ == '__main__':
	print("Count cards")
	# Import each printing of each card
	data = import_scryfall("default-cards-20220722090459.json")
	# data = import_scryfall("some_cards.json")

	condition_mythic = count_condition.Condition('rarity', 'mythic')
	condition_paper = count_condition.ConditionList('games', 'paper')
	printing_conditions = [condition_mythic, condition_paper]

	mythic_cards = count_printings(data, printing_conditions=printing_conditions)
	# prepare_cards_for_export(mythic_cards)
	cool_stuff.write_data_dictionary(mythic_cards, "cards")
