from unidecode import unidecode
from magic_grinder_02_match_data import controller_get_sorted_data
from shared_methods_io import *
from shared_methods_grinder import *
from import_scryfall_bulk_data import *
from shared_methods_grinder_03 import get_usd_from_card_03, get_price_range_03
from magic_grinder_03_call_api import call_scryfall_03


class NewCard:
	scryfall_card = {}
	card = {}

	name = ""
	set = ""
	collector_number = ""
	foil = False

	def __init__(self, card):
		self.reset_card(card)

		self.try_reset_name()
		self.try_reset_set()
		self.try_reset_collector_number()
		self.try_reset_foil()

	def try_match_self(self, data):
		has_name = len(self.name) > 0
		has_set = len(self.set) > 0
		has_set_num = len(self.collector_number) > 0

		if has_name and has_set and has_set_num:
			return self.match_self_full(data)
		elif has_name:
			return self.match_self_abridged(data)

	def match_self_full(self, data):
		try:
			if self.set not in data.keys():
				print(f"Errant operation! Could not find set {self.set} for card {self.name}")
				return False

			matched_card = next(
				(item for item in data[self.set] if
				 unidecode(item['name']) == unidecode(self.name)
				 and item['collector_number'] == self.collector_number), None)

			if matched_card is not None:
				self.scryfall_card = matched_card
				return True
			else:
				print(f"Could not find card: '{self.name}' in set '{self.set}'")
				return False
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
			elif field == "set_num" or field == "set_no" or field == "collector_number":
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
				return ""
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
				year = str(datetime.today().year)
				if "year" in self.card:
					if self.card["year"] is None or len(self.card["year"]) == 0:
						return year
					else:
						return self.card["year"]
				else:
					return year
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


def match_cards_03(data_sorted, all_cards, match_fields_raw):
	output_cards = []
	failed_cards = []

	match_fields = []
	# If called from controller_process_over_cards_in_file, this information will already be sanitized.
	#     But the code doesn't know that
	for field in match_fields_raw:
		match_fields.append(snake_case_parameter(field))

	standardize_header_names(headers=match_fields)

	# Iterates through each card in the all_cards list
	for card in all_cards:
		try:
			# Some input files include a count row. If this row exists and is equal to 0, skips the card
			if 'count' in card and int(card['count']) <= 0:
				continue

			this_card = NewCard(card)
			new_row = []

			if this_card.try_match_self(data_sorted):
				# print("Found card!")
				for match_field in match_fields:
					new_row.append(this_card.try_get_field(match_field))

				output_cards.append(new_row)
			else:
				failed_cards.append(card)


		# print("Yearning 4 my bestie")
		# print(this_card.scryfall_card["oracle_id"])

		except Exception as E:
			print(f"Errant operation parsing card {card['name']}")
			print(E)
			failed_cards.append(card)

	# Outputs success / failure
	if len(output_cards) > 0:
		print(f"Success! Bound {len(output_cards)} cards")
	else:
		print("Failure! No cards bound!")

	if len(failed_cards) == 0:
		print("No cards failed!")
	else:
		print(f"{len(failed_cards)} card(s) failed")
	# print(failed_cards)

	return output_cards


# For the given filename, runs match_cards_03 where the match fields are the same as the csv columns
def controller_process_cards_in_file(filename, data, match_fields=None):
	if match_fields is None:
		match_fields = []
	print("Matching cards to audit data")

	# data = import_scryfall_abridged()
	all_cards = read_csv(filename, True, True)

	if len(match_fields) == 0:
		match_fields = read_csv_get_headers(name=filename, do_standardize_header_names=True, do_snake_case_names=True)

	audit_rows = match_cards_03(data, all_cards, match_fields)

	audit_rows_with_headers = []
	if len(match_fields) > 0:
		audit_rows_with_headers.append(match_fields)
	else:
		audit_rows_with_headers.append(read_csv_get_headers(name=filename))

	for audit_row in audit_rows:
		audit_rows_with_headers.append(audit_row)

	write_data_list(audit_rows_with_headers, "audit")


def controller_process_cards_from_api(request_url, match_fields_raw, display_fields=""):
	print("Matching cards from API")

	match_fields = []
	# If called from controller_process_over_cards_in_file, this information will already be sanitized.
	#     But the code doesn't know that
	for field in match_fields_raw:
		match_fields.append(snake_case_parameter(field))

	# Assigns the first row of the output rows list to display fields if it exists. Otherwise the match fields
	audit_rows = []
	if len(display_fields) > 0:
		audit_rows.append(display_fields)
	else:
		audit_rows.append(match_fields)

	do_process_cards_from_api(request_url, match_fields, audit_rows)

	write_data_list(audit_rows, "api_cards")


def do_process_cards_from_api(request_url, match_fields, audit_rows):
	payload = call_scryfall_03(request_url=request_url)
	for scryfall_card in payload["data"]:
		card = {"name": scryfall_card["name"], "set": scryfall_card["set"],
		        "collector_number": scryfall_card["collector_number"]}
		this_card = NewCard(card)
		this_card.try_assign_card(scryfall_card)
		new_row = []
		for match_field in match_fields:
			new_row.append(this_card.try_get_field(match_field))

		audit_rows.append(new_row)

	if payload["has_more"]:
		do_process_cards_from_api(payload["next_page"], match_fields, audit_rows)


if __name__ == '__main__':
	print("Welcome to Magic Grinder version Three!")
	filename = "all_unique_mv_cards.csv"

	# data = controller_get_sorted_data()
	# data = import_scryfall_abridged()
	data = controller_get_original_printings()

	# filename = "all_audit_cards.csv"
	# match_fields = ["name", "set", "set_num", "frame", "value"]
	match_fields = ["name", "set", "set_num", "mana_cost", "released_at"]
	# search_url = "https://api.scryfall.com/cards/search?q=set%3A2x2+r%3Ac+new%3Ararity"
	# search_url = "https://api.scryfall.com/cards/search?q=otag%3Aunique-mana-cost"
	# controller_process_cards_from_api(search_url, match_fields)
	controller_process_cards_in_file(filename, data, match_fields)
