from unidecode import unidecode
from shared_methods_io import *
from shared_methods_grinder import *
from import_scryfall_bulk_data import *
from shared_methods_grinder_03 import get_usd_from_card_03, get_price_range_03
from magic_grinder_03_call_api import call_scryfall_03, get_set_search_uri_from_set_code
from datetime import *
from magic_sorter_03 import MagicSorterTrie03


class NewCard:
	scryfall_card = {}
	card = {}

	name = ""
	set = ""
	collector_number = ""
	foil = False
	sorter_id = 0

	# Extra fields used by the Sorter. I would love to take out sort_codes and have it calculated as-needed
	# sorter_id = 0
	# sort_codes = {}

	def __init__(self, card):
		self.reset_card(card)

		self.try_reset_name()
		self.try_reset_set()
		self.try_reset_collector_number()
		self.try_reset_foil()
		self.sorter_id = 0
		self.sort_codes = {}

	def __str__(self):
		return self.name

	def try_match_self(self, data):
		has_name = len(self.name) > 0
		has_set = len(self.set) > 0
		has_set_num = len(self.collector_number) > 0
		has_frame = "frame" in self.card and len(self.card["frame"]) > 0

		# TODO: Defaults to match_self_abridged if data is abridged
		if has_name and has_set and has_set_num:
			return self.match_self_full(data)
		if has_name and has_set and has_frame:
			return self.match_self_frame(data)
		elif has_name:
			return self.match_self_abridged(data)

	def match_self_full(self, data):
		try:
			if self.set not in data.keys():
				print(f"Errant operation! Could not find set {self.set} for card {self.name}")
				return False
			else:
				matched_set = data[self.set]
				for card in matched_set:
					if unidecode(card["name"]) == unidecode(self.name) and card[
						"collector_number"] == self.collector_number:
						self.scryfall_card = card
						self.set = card["set"]
						self.collector_number = card["collector_number"]
						return True
				print(f"Errant operation! Could not find card {self.name} in set {self.set}")
		# if self.set not in data.keys():
		# 	print(f"Errant operation! Could not find set {self.set} for card {self.name}")
		# 	return False
		#
		# matched_card = next(
		# 	(item for item in data[self.set] if
		# 	 unidecode(item['name']) == unidecode(self.name)
		# 	 and item['collector_number'] == self.collector_number), None)
		#
		# if matched_card is not None:
		# 	self.scryfall_card = matched_card
		# 	return True
		# else:
		# 	print(f"Could not find card: '{self.name}' in set '{self.set}'")
		# 	return False
		except Exception as E:
			print("Errant operation matching card")
			print(E)
			return False

	def match_self_abridged(self, data):
		try:
			matched_card = next(
				(item for item in data if unidecode(item['name']) == unidecode(self.name)), None)

			if matched_card is not None:
				self.scryfall_card = matched_card
				self.set = matched_card["set"]
				self.collector_number = matched_card["collector_number"]
				return True
			else:
				print(f"Could not find card: '{self.name}'")
				return False

		except Exception as E:
			print("Errant operation matching card")
			print(E)
			return False

	def match_self_frame(self, data):
		try:
			if self.set not in data.keys():
				print(f"Errant operation! Could not find set {self.set} for card {self.name}")
				return False
			else:
				matched_set = data[self.set]
				frame = self.card["frame"]
				for card in matched_set:
					if unidecode(card["name"]) == unidecode(self.name):
						card_frame = get_card_variant(card)
						if card_frame == frame:
							self.scryfall_card = card
							self.set = card["set"]
							self.collector_number = card["collector_number"]
							return True
				print(f"Errant operation! Could not find card {self.name} in set {self.set}")

		except Exception as E:
			print("Errant operation matching card")
			print(E)
			return False

	# For cards returned from the API, the scryfall_card field can be assigned directly
	def try_assign_card(self, scryfall_card):
		self.scryfall_card = scryfall_card
		return True

	# Creates a copy of the parameterized card dictionary where each key is snake-cased
	#    and assigns that copy to the self.card field
	def reset_card(self, card):
		new_card = {}
		# TODO: try to run the headers through the shared_methods_io.standardize_header_names
		for key in card:
			new_card[snake_case_parameter(key)] = card[key]

		self.card = new_card

	def try_reset_name(self):
		if "name" in self.card:
			self.name = self.card["name"]
		else:
			self.name = ""

	def try_reset_set(self):
		if "set" in self.card:
			self.set = self.card["set"].lower()
		elif "set_name" in self.card:
			self.set = self.card["set_name"].lower()
		else:
			self.set = ""

	def try_reset_collector_number(self):
		if "set_num" in self.card:
			self.collector_number = self.card["set_num"]
		elif "set_no" in self.card:
			self.collector_number = self.card["set_no"]
		elif "collector_number" in self.card:
			self.collector_number = self.card["collector_number"]
		else:
			self.collector_number = ""

	def try_reset_foil(self):
		foil_str = ""
		if "foil" in self.card:
			foil_str = self.card["foil"]
		elif "is_foil" in self.card:
			foil_str = self.card["is_foil"]

		if foil_str == "1":
			self.foil = True
		elif foil_str.lower() == "true":
			self.foil = True
		else:
			self.foil = False

	# This important logical method attempts to parse the requested field and return it as best it can.
	# The heirarchy of logic is this: first it attempts to return basic card information, then it looks if the field
	#     has any custom logic associated with it, then it attempts to get basic scryfall_card data. If that returns
	#     empty it checks the self.card. If it can't find the field there it returns an empty string
	def try_get_field(self, field):
		try:
			if field == "name":
				return self.name
			elif field == "set" or field == "set_name":
				return self.set.upper()
			elif field == "set_num" or field == "set_no" or field == "set_number" or field == "collector_number":
				return self.collector_number
			# It is presumed that, if this method is being called instead of accessing the field directly, that
			#     this information is going to be output to Excel. Therefore, this field is returned as a string
			elif field == "foil" or field == "is_foil":
				if self.foil:
					return "1"
				else:
					return "0"
			# Fixes an amusing error where the logic would populate this field with the extremely long scryfall ID
			elif field == "id":
				return str(self.sorter_id)
			# If you need the Scryfall ID field, you have to enter 'Scryfall_Id' because I've already established ID
			#     as my ordering number and I'm not changing it
			elif field == "scryfall_id":
				return self.scryfall_card["id"]
			elif field == "frame" or field == "variant":
				return get_card_variant(self.scryfall_card)
			elif field == "spc":
				variant = get_card_variant(self.scryfall_card)
				if "Frame" in variant:
					return "0"
				else:
					return "1"
			elif field == "price_range":
				# Thought about doing this recursively, then I was like, naaaah
				value = self.try_get_field_value()
				rarity = self.try_get_field_rarity()
				return get_price_range_03(value=value, rarity=rarity)
			elif field == "section":
				return assign_default_section(self.scryfall_card)
			elif field == "year":
				this_year = str(datetime.today().year)
				if "year" in self.card:
					if self.card["year"] is None or len(self.card["year"]) == 0:
						return this_year
					else:
						return self.card["year"]
				else:
					return this_year
			elif field == "input_code" or field == "code":
				return f"{self.name} ({self.set}) {self.collector_number}"
			elif field == "r" or field == "rarity":
				return self.try_get_field_rarity()
			elif field == "card_type" or field == "type":
				return get_card_type_from_type_line(self.scryfall_card["type_line"])
			elif field == "c" or field == "color" or field == "colors":
				return get_color_code_from_colors(get_field_from_card("colors", self.scryfall_card))
			elif field == "c_id" or field == "color_id":
				return get_color_code_from_colors(get_field_from_card("color_identity", self.scryfall_card))
			elif field == "produces" or field == "mana" or field == "produced_mana":
				produced_mana = get_field_from_card("produced_mana", self.scryfall_card, not_found="none")
				if produced_mana != "none":
					return get_color_code_from_colors(produced_mana)
				else:
					return ""
			elif field == "code":
				return f"{self.set.upper()}|{self.collector_number}"
			elif field == "value" or field == "price":
				return self.try_get_field_value()

			# Checks if field is in scryfall object. If so, returns that field
			scryfall_card_field = str(get_field_from_card(scryfall_card=self.scryfall_card, field=field))
			if len(scryfall_card_field) > 0:
				return scryfall_card_field
			# Checks if field is in default card
			elif field in self.card:
				return self.card[field]
			# If it can't find the field anywhere, returns empty string
			else:
				return ""
		# Returns an error string if any part in the process throws an error. This is an important improvement of V02
		#     where before the entire card would fail.
		except Exception as E:
			print(f"Errant operation calculating field {field} for card {self.name}")
			print(E)
			return f"ERROR | {E}"

	def try_get_field_value(self):
		return get_usd_from_card_03(self, self.scryfall_card)

	def try_get_field_rarity(self):
		return get_field_from_card("rarity", self.scryfall_card)[0].upper()


# Receives a reference to a file. Imports and matches cards from that file
# Returns list of bound NewCard objects
def get_cards_from_file(filename, data):
	print(f"Importing cards from {filename}")
	all_cards = read_csv(filename, True, True)
	output_cards = []
	failed_cards = []

	for card in all_cards:
		try:
			# Some input files include a count row. If this row exists and is equal to 0, skips the card
			if 'count' in card and int(card['count']) <= 0:
				continue

			this_card = NewCard(card)

			if this_card.try_match_self(data):
				output_cards.append(this_card)
			else:
				failed_cards.append(this_card)

		except Exception as E:
			print(f"Errant operation parsing card {card['name']}")
			print(E)
			failed_cards.append(card)

	if len(output_cards) > 0:
		print(f"Success! Bound {len(output_cards)} cards")
	else:
		print("Failure! No cards bound!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")

	return output_cards


# Receives a Scryfall API endpoint. Gets all cards from that endpoint
# Returns list of bound NewCard objects
def get_cards_from_api(request_url):
	print(f"Matching cards from API endpoint {request_url}")
	output_cards = []
	return do_get_new_cards_from_api(request_url, output_cards)


# A recursive method to retrieve cards from the given API, then recurse if there are any cards left
def do_get_new_cards_from_api(request_url, output_cards):
	try:
		payload = call_scryfall_03(request_url=request_url)

		# For each card in the data payload, creates a new card object
		for scryfall_card in payload["data"]:
			card = {"name": scryfall_card["name"], "set": scryfall_card["set"],
			        "collector_number": scryfall_card["collector_number"]}
			this_card = NewCard(card)
			this_card.try_assign_card(scryfall_card)

			output_cards.append(this_card)

		# If there are more cards, recurses. Otherwise returns
		if payload["has_more"]:
			return do_get_new_cards_from_api(payload["next_page"], output_cards)
		else:
			return output_cards

	except Exception as E:
		print("Errant operation returning cards from API")
		print(E)
		return None


# Receives a list of bound NewCard objects. Sorts them using magic_grinder_03 and the given sort logic file
# Returns the same NewCard objects in a sorted order
def sort_all_cards(all_cards, sort_logic_filename):
	print("Sorting cards!")
	SortAudit = MagicSorterTrie03(sort_logic_filename)

	for card in all_cards:
		SortAudit.add_card(card)

	return SortAudit.output_cards()


# Process cards for the given match fields
# Returns a list of lists (without a header row)
def output_bound_cards(all_cards, match_fields_raw, count_field=""):
	print(f"Processing cards with these fields: {', '.join(match_fields_raw)}")

	output_rows = []
	failed_cards = []
	do_count = len(count_field) > 0

	match_fields = []
	# If called from controller_process_over_cards_in_file, this information will already be sanitized.
	#     But the code doesn't know that
	for field in match_fields_raw:
		match_fields.append(snake_case_parameter(field))

	for new_card in all_cards:
		try:
			# Some input files include a count row. If this row exists and is equal to 0, skips the card
			if do_count:
				card_count = new_card.try_get_field(count_field)
				if len(card_count) == 0 or card_count == "0":
					continue

			new_row = []
			for match_field in match_fields:
				new_row.append(new_card.try_get_field(match_field))

			# If there is a count_field, output the completed new row for each value of the count field
			if do_count:
				card_count = new_card.try_get_field(count_field)
				num_count = int(card_count)
				for i in range(num_count):
					output_rows.append(new_row)
			else:
				output_rows.append(new_row)
		except Exception as E:
			print(f"Errant operation parsing card {new_card.name}")
			print(E)
			failed_cards.append(new_card)

	if len(output_rows) > 0:
		print(f"Success! Processed {len(output_rows)} rows")
	else:
		print("Failure! No rows processed!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")
	# print(failed_cards)

	return output_rows


def new_controller_process_cards_from_file(filename, data, match_fields=None, count_field="", do_sort=False):
	# Imports all cards from given filename
	all_new_cards = get_cards_from_file(filename, data)

	# Does some shit to prepare the match fields and headers
	header_row = []
	if match_fields is None or len(match_fields) == 0:
		match_fields = read_csv_get_headers(name=filename, do_standardize_header_names=True, do_snake_case_names=True)
		header_row = read_csv_get_headers(name=filename)
	else:
		header_row = match_fields

	# If parameterized do_sort is true, overrides all_new_cards with a sorted version of itself
	if do_sort:
		all_new_cards = sort_all_cards(all_new_cards, "sorter_logic_03.json")
	# For the given fields, prepares an output row for each card.

	output_rows = output_bound_cards(all_new_cards, match_fields, snake_case_parameter(count_field))

	# Prepends output rows with header row and outputs to CSV
	output_rows.insert(0, header_row)
	write_data_list(output_rows, "audit")


# Processes cards from a given API endpoint with the given fields. Unlike process_from_file, match fields is required
def new_controller_process_cards_from_api(request_url, match_fields):
	all_new_cards = get_cards_from_api(request_url)

	# if do_sort:
	# 	all_new_cards = sort_all_cards(all_new_cards, "sorter_logic_03.json")

	output_rows = output_bound_cards(all_new_cards, match_fields)

	output_rows.insert(0, match_fields)
	write_data_list(output_rows, "api_cards")


# A controller for my use only with no parameters. Takes multiple files and combines them.
def controller_process_cards_from_multiple_files():
	data = controller_get_sorted_data()

	all_audit_cards = get_cards_from_file("audit_csv.csv",data)
	all_test_cards = get_cards_from_file("audit_csv.csv", data)

	all_new_cards = all_audit_cards
	for card in all_test_cards:
		all_new_cards.append(card)

	all_new_cards = sort_all_cards(all_new_cards, "sorter_logic_03.json")

	match_fields = read_csv_get_headers(name=filename, do_standardize_header_names=True, do_snake_case_names=True)
	header_row = read_csv_get_headers(name=filename)

	output_rows = output_bound_cards(all_new_cards, match_fields)

	# Prepends output rows with header row and outputs to CSV
	output_rows.insert(0, header_row)
	write_data_list(output_rows, "combined")


if __name__ == '__main__':
	print("Welcome to Magic Grinder version Three!")

	# filename = "all_order_cards.csv"
	filename = "audit_csv.csv"
	# filename = "all_test_cards.csv"

	# request_url = get_set_search_uri_from_set_code('woe')

	# data = controller_get_sorted_data("default-cards")
	# data = controller_get_sorted_data("test-cards")
	# data = import_scryfall_abridged()
	# data = controller_get_original_printings()

	# match_fields = ["name", "set", "set_num", "rarity", "card_type", "color", "frame", "value"]
	# match_fields = ["name", "set", "set_num", "mana_cost", "released_at"]
	controller_process_cards_from_multiple_files()
	# new_controller_process_cards_from_file(filename, data, do_sort=True)
# new_controller_process_cards_from_file(filename, data, count_field="count", do_sort=True)
# new_controller_process_cards_from_api(request_url, match_fields)
