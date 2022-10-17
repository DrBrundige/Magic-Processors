from magic_grinder_get_card_features import *


def bind_audit_cards_usd(data, rarities, source_cards="all_audit_cards.csv"):
	all_cards = cool_stuff.read_csv(source_cards)
	bound_cards = []
	failed_cards = []

	for card in all_cards:
		try:

			card_rarity = card["rarity"][0].upper()
			if card_rarity not in rarities:
				continue

			scryfall_card = next(
				(item for item in data if item['name'] == card['name']
				 and item['collector_number'] == card['collector_number']
				 and item['set'].lower() == card['set'].lower()), None)

			if scryfall_card is None:
				print("Errant operation! Could not find card: " + card['name'])
				failed_cards.append(card['name'])
				continue

			new_line = {'name': card['name'], 'set': scryfall_card['set'].upper(),
			            'set_num': scryfall_card['collector_number'], 'rarity': card['rarity'],
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
			print(f"{card['name']} | {new_line['price']}")
			bound_cards.append(new_line)

		except Exception as E:
			print(f"Errant operation parsing card {card['name']}")
			print(E)
			failed_cards.append(card['name'])

	return bound_cards


if __name__ == '__main__':
	print("Valuing collection")

	# Import each printing of each card
	data = import_scryfall("default-cards-20220919210802.json")
	print("Imported cards!")

	prices = bind_audit_cards_usd(data, ["R", "M"], "all_audit_cards.csv")
	cool_stuff.write_data(prices, "prices")
