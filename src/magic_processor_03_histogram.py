from magic_processor_03 import get_all_cards_from_data_file, get_cards_from_api, get_cards_from_file
from common_methods_io import *
from common_methods_processor import *
from import_scryfall_bulk_data import *
from common_methods_processor_03 import get_usd_from_card_03, get_price_range_03
from common_methods_call_scryfall import *
from datetime import *
from magic_sorter_03 import MagicSorterTrie03


# Accepts a list of new_card objects, a single match field, and a histogram
def output_histogram(all_cards, match_field, histogram=None, do_split_faces=False):
	if histogram is None:
		histogram = {}

	for new_card in all_cards:
		if do_split_faces and "card_faces" in new_card.scryfall_card:
			faces = new_card.scryfall_card["card_faces"]
			for face in faces:
				this_output = face[match_field]
				if this_output in histogram:
					histogram[this_output] = histogram[this_output] + 1
				else:
					histogram[this_output] = 1

		else:
			this_output = new_card.try_get_field(match_field)
			if this_output in histogram:
				histogram[this_output] = histogram[this_output] + 1
			else:
				histogram[this_output] = 1

	return histogram


# Accepts a list of new_card objects, a single match field, and a histogram
def custom_histogram_creature_types(all_cards):
	all_creature_types = controller_get_scryfall_creature_types()
	histogram = {}
	for creature_type in all_creature_types:
		histogram[creature_type] = 0

	for new_card in all_cards:
		this_output = new_card.try_get_field("type_line")
		for type in this_output.split(" "):
			if type in histogram:
				histogram[type] = histogram[type] + 1

	return histogram


def controller_process_histogram_from_data_file(data, match_field, output_name="scan", do_split_faces=False):
	all_cards = get_all_cards_from_data_file(data)
	populated_histogram = output_histogram(all_cards, match_field, do_split_faces=do_split_faces)
	write_data_dictionary(populated_histogram, filename=output_name)


def controller_process_histogram_from_api(request_url, match_field, output_name="scan"):
	all_cards = get_cards_from_api(request_url)
	populated_histogram = output_histogram(all_cards, match_field)
	# populated_histogram = custom_histogram_creature_types(all_cards)
	write_data_dictionary(populated_histogram, filename=output_name)


def controller_process_histogram_from_sheet(filename, data, match_field, output_name="scan"):
	all_cards = get_cards_from_file(filename=filename, data=data)
	populated_histogram = output_histogram(all_cards, match_field)
	write_data_dictionary(populated_histogram, filename=output_name)


if __name__ == '__main__':
	# data = import_scryfall("eternal-cards")
	data = controller_get_sorted_data()
	# filename = "audit_csv.csv"
	# request_url = get_set_search_uri_from_set_code("OTJ")
	# set = "mkm"
	# request_url = f"https://api.scryfall.com/cards/search?include_extras=true&order=set&q=e%3A{set}+game%3Apaper"
	# request_url = "https://api.scryfall.com/cards/search?include_extras=true&order=set&" \
	#               "q=type%3Acreature+type%3Aelder+game%3Apaper+f%3Avintage&unique=cards&as=grid&order=name"
	match_field = "mana_cost"
	# controller_process_histogram_from_sheet(filename, data, match_field)
	# controller_process_histogram_from_api(request_url, match_field)
	controller_process_histogram_from_data_file(data, match_field, do_split_faces=True)
