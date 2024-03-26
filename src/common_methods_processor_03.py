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
