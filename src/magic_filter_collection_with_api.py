from common_methods_io import read_csv, write_data_list
from common_methods_requests import call_scryfall_03
from magic_processor_03 import NewCard, output_bound_cards


def bind_cards_from_api_and_file(filename, terms):
	# Import audit sheet
	print("Reading cards from sheet")
	all_cards = read_csv(filename, True, True)

	# Return API data
	request_url = get_query_from_terms(terms)
	print(f"Matching cards from API endpoint {request_url}")
	api_cards = []
	do_get_new_cards_from_api_list(request_url, api_cards)

	# Match audit cards with API data

	cards_dictionary = {}

	for scryfall_card in api_cards:
		cards_dictionary[scryfall_card["name"]] = scryfall_card

	matched_cards = []

	for csv_card in all_cards:
		name = csv_card['name']
		if name in cards_dictionary:
			# print(csv_card['name'])
			this_card = NewCard(csv_card)
			this_card.try_assign_card(cards_dictionary[name])
			matched_cards.append(this_card)

	return matched_cards


def get_query_from_terms(terms):
	if len(terms) == 0:
		return False

	combined_terms = []

	for key, value in terms.items():
		this_term = f"{key}%3A{process_multiple_words(value)}"
		combined_terms.append(this_term)

	terms_string = "+".join(combined_terms)
	# print(terms_string)
	return f"https://api.scryfall.com/cards/search?q={terms_string}&unique=cards&as=grid"


def process_multiple_words(value):
	if " " in value:
		return f"\'{value.replace(' ', '+')}\'"
	else:
		return value


# Calls API and returns all cards as a single list of dictionaries.
# This is actually identical code to bulk_data_create.do_get_json
# I don't love this redundancy. There are several slight variations on this method.
# Perhaps I could consolidate and have them all use this method
# and then loop through the finished object but it's fine for now
def do_get_new_cards_from_api_list(request_url, output_cards):
	try:
		payload = call_scryfall_03(request_url=request_url)
		for card_object in payload['data']:
			output_cards.append(card_object)

		if payload["has_more"]:
			return do_get_new_cards_from_api_list(payload["next_page"], output_cards)
		else:
			return output_cards
	except Exception as E:
		print(f"Errant operation getting test data from API!")
		print(E)


def controller_filter_collection_with_api(filename, terms, match_fields):
	all_bound_cards = bind_cards_from_api_and_file(filename=filename, terms=terms)

	output_rows = output_bound_cards(all_bound_cards, match_fields)

	output_rows.insert(0, match_fields)
	write_data_list(output_rows, "filter")


# Output match fields

if __name__ == '__main__':
	print("Filtering decklist by API call")
	filename = "audit_csv.csv"
	# terms = {"id": "gu", "otag": "untapper-creature", "f": "commander"}
	terms = {"artist": "Magali Villeneuve"}
	match_fields = ["name", "set", "type", "home_box", "2024_audit", "edhrec_rank", "mana_cost", "oracle_text"]
	controller_filter_collection_with_api(filename=filename, terms=terms, match_fields=match_fields)
