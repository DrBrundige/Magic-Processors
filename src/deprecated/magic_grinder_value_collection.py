from ..shared_methods_grinder import *
from ..import_scryfall import import_scryfall_full
from src.deprecated.sort_card_data import sort_cards_by_set
from unidecode import unidecode


# Data - Requires the full default-cards dataset sorted with the sort_cards_by_set
# Inputs cards from a bulk set sheet: name, count (optional), foil, collector_number, set
# Outputs largely the same information plus price data
# name - input
# set - input
# set_num - input
# rarity - output
# foil - input
# variant - output
# price - output
# price_type - output
def bind_audit_cards_usd(data_sorted, source_cards="all_audit_cards.csv"):
	all_cards = cool_stuff.read_csv(source_cards)
	bound_cards = []
	failed_cards = []

	for card in all_cards:
		try:

			# card_rarity = card["rarity"][0].upper()
			# if card_rarity not in rarities:
			# 	continue

			if 'count' in card and int(card['count']) <= 0:
				continue

			scryfall_card = next(
				(item for item in data_sorted[card['set'].lower()] if
				 unidecode(item['name']) == unidecode(card['name'])
				 and item['collector_number'] == card['collector_number']), None)

			if scryfall_card is None:
				print("Errant operation! Could not find card: " + card['name'])
				failed_cards.append(card)
				continue

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
			# print(f"{card['name']} | {new_line['price']}")

			if 'count' in card and int(card['count']) > 1:
				for i in range(int(card['count'])):
					bound_cards.append(new_line)
			else:
				bound_cards.append(new_line)

		except Exception as E:
			print(f"Errant operation parsing card {card['name']}")
			print(E)
			failed_cards.append(card)

	# Outputs success / failure
	if len(bound_cards) > 0:
		print(f"Success! Bound {len(bound_cards)} cards")
	else:
		print("Failure! No cards bound!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")
		print(failed_cards)

	return bound_cards


if __name__ == '__main__':
	print("Valuing collection")

	# Import each printing of each card
	data = import_scryfall_full()
	print("Imported cards!")
	data_sorted = sort_cards_by_set(data)
	print("Sorted cards!")

	prices = bind_audit_cards_usd(data_sorted, "all_library_cards.csv")
	cool_stuff.write_data(prices, "prices")
