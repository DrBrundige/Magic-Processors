import re

from common_methods_io import read_txt, write_data, write_data_list, write_data_to_txt, snake_case_parameter_list
from common_methods_call_scryfall import call_scryfall_03
from common_methods_grinder import get_color_code_from_colors
from import_scryfall_bulk_data import import_scryfall_abridged
from process_custom_card_sheet import process_colors_from_mana_cost, process_mana_value_from_mana_cost

REGEX_REPRINT = re.compile("\(Reprint\)")  # Validates that the string is the word (Reprint)
REGEX_PT = re.compile("(^.{1,2}/.{1,2}$)")  # Validates that the string is power / toughness
REGEX_FLAVOR = re.compile("(^-{4,9}$)")  # Validates that the string is the underbar separating rules from flavor text
REGEX_COLOR = re.compile("(^\(.*\)$)")
REGEX_SYMBOL = re.compile("(^\{.*\}$)")


class CustomCard:
	card_header = ""
	rarity = ""
	block = [""]

	rarities = {"C": "common", "U": "uncommon", "R": "rare", "M": "mythic rare"}

	def __init__(self, card_header, block, rarity):
		self.card_header = card_header
		self.block = block
		self.rarity = rarity

	def __str__(self):
		return self.card_header

	def try_get_field(self, field):
		try:
			if field == "header":
				return self.card_header
			elif field == "card_body":
				body = self.block.copy()
				body.pop(0)
				body.pop(0)
				return "\n".join(body)
			elif field == "rarity":
				return self.try_get_rarity()
			elif field == "flavor":
				return " ".join(self.try_get_flavor())

			else:
				return ""
		# Returns an error string if any part in the process throws an error.
		except Exception as E:
			print(f"Errant operation calculating field {field} for card {self.card_header}")
			print(E)
			return f"ERROR | {E}"

	def try_get_field_mse(self, field):
		return_string = ""

		if field == "name":
			return_string = self.try_get_field("name")
		elif field == "casting_cost":
			return_string = self.try_get_field("mana_cost")
		elif field == "super_type":
			type_line = self.try_get_field("type_line")
			split_types = type_line.split("-")
			return_string = split_types[0].strip()
		elif field == "sub_type":
			type_line = self.try_get_field("type_line")
			split_types = type_line.split("-")
			if len(split_types) > 1:
				return_string = split_types[1].strip()
		elif field == "rarity":
			return_string = self.try_get_field("rarity")
			if return_string in self.rarities:
				return_string = self.rarities[return_string]

		elif field == "rule_text":
			return_string = self.try_get_field("rules")
			# Clears any brackets from the rules text. MSE can parse the symbols automatically
			return_string = return_string.replace("{", "")
			return_string = return_string.replace("}", "")
			if "\n" in return_string:
				return_string = return_string.replace("\n", "\n\t\t")
				return f"\t{field}:\n\t\t{return_string}"
		elif field == "power":
			return_string = self.try_get_field("power")
		elif field == "toughness":
			return_string = self.try_get_field("toughness")
		elif field == "flavor_text":
			return_string = " ".join(self.try_get_field("flavor"))

		if len(return_string) > 0:
			return f"\t{field}: {return_string}"
		else:
			return ""

	def try_get_flavor(self):
		flavor_row = find_regex_in_list(self.block, REGEX_FLAVOR)
		if flavor_row > -1:
			return self.block[flavor_row + 1:len(self.block)]
		else:
			return ""

	def try_get_rarity(self):
		split_type = self.block[1].split("|")
		if len(split_type) > 1:
			return str.strip(split_type[1])[0]
		else:
			return self.rarity


class CustomCardSheet(CustomCard):

	def __init__(self, card_header, block, rarity):
		super().__init__(card_header, block, rarity)

	def try_get_field(self, field):
		try:
			return_text = super().try_get_field(field=field)
			if len(return_text) > 0:
				return return_text

			elif field == "name":
				return self.try_get_name()
			elif field == "type_line":
				return self.try_get_type_line()
			elif field == "mana_cost":
				return self.try_get_mana_cost()
			elif field == "cmc":
				return self.try_get_cmc()
			elif field == "color" or field == "color_identity":
				return self.try_get_color()
			elif field == "rules":
				return self.try_get_rules()
			elif field == "pt":
				return self.try_get_pt()
			elif field == "power":
				return self.try_get_power()
			elif field == "toughness":
				return self.try_get_toughness()
			else:
				return ""

		# Returns an error string if any part in the process throws an error.
		except Exception as E:
			print(f"Errant operation calculating field {field} for card {self.card_header}")
			print(E)
			return f"ERROR | {E}"

	# Perhaps some day I can start putting the correct notation for mana in the cost section, but I'm too lazy right now
	def try_get_name(self):
		split_name = self.card_header.split()
		split_name.pop(-1)
		name_without_mana = " ".join(split_name)
		return name_without_mana

	def try_get_mana_cost(self):
		split_name = self.card_header.split()
		cost = split_name.pop()

		m = REGEX_COLOR.fullmatch(cost)
		if m is not None:
			return ""
		else:
			return cost

	def try_get_cmc(self):
		split_name = self.card_header.split()
		cost = split_name.pop()

		m = REGEX_COLOR.fullmatch(cost)
		if m is not None:
			return ""
		else:
			return str(process_mana_value_from_mana_cost(cost))

	def try_get_type_line(self):
		split_type = self.block[1].split("|")

		return str.strip(split_type[0])

	def try_get_color(self):
		split_name = self.card_header.split()
		cost = split_name.pop()

		return process_colors_from_mana_cost(cost)

	def try_get_rules(self):
		pt_row = find_regex_in_list(self.block, REGEX_PT)
		flavor_row = find_regex_in_list(self.block, REGEX_FLAVOR)
		if pt_row > -1:
			if flavor_row > -1:
				# Both pt and flavor found. Return whichever is smaller
				if pt_row > flavor_row:
					# It occurs to me there is basically no reason why a pt would come after the flavor... but for robustness
					return "\n".join(self.block[2:flavor_row])
				else:
					return "\n".join(self.block[2:pt_row])
			else:
				return "\n".join(self.block[2:pt_row])
		else:
			# No pt found, but flavor was found. Return until flavor
			if flavor_row > -1:
				return "\n".join(self.block[2:flavor_row])
			else:
				# Neither pt nor flavor bar found. Return until end
				return "\n".join(self.block[2:len(self.block)])

	def try_get_pt(self):
		pt_row = find_regex_in_list(self.block, REGEX_PT)
		if pt_row > -1:
			return self.block[pt_row]
		else:
			return ""

	# Originally I wasn't going to add these, but then I realized that Excel auto-formats the PT as a date LMAO FFS.
	def try_get_power(self):
		pt = self.try_get_pt()
		if len(pt) > 0:
			pt_list = pt.split("/")
			return pt_list[0]
		else:
			return ""

	def try_get_toughness(self):
		pt = self.try_get_pt()
		if len(pt) > 0:
			pt_list = pt.split("/")
			return pt_list[1]
		else:
			return ""


class CustomCardReprint(CustomCard):
	scryfall_object = {}

	def __init__(self, card_header, block, rarity):
		super().__init__(card_header, block, rarity)
		self.try_get_card_from_scryfall()

	# Retrieves a card with the same name from the Scryfall API.
	# I assumed this would be faster than importing the full bulk data, but I forgot how many reprints I have in my set.
	def try_get_card_from_scryfall(self):
		split_name = self.card_header.split()
		split_name.pop(-1)
		name_without_mana = "+".join(split_name)
		data = call_scryfall_03(endpoint=f'cards/search?q=%21"{name_without_mana}"')
		if data is not None:
			if data["total_cards"] > 0:
				print("Found card <3")
				self.scryfall_object = data["data"][0]
				return True
			else:
				return False
		else:
			return False

	def try_get_field(self, field):
		try:
			return_text = super().try_get_field(field=field)
			if len(return_text) > 0:
				return return_text
			elif field == "rules":
				return self.scryfall_object["oracle_text"]
			elif field == "color" or field == "color_identity":
				return get_color_code_from_colors(self.scryfall_object["color_identity"])
			elif field in self.scryfall_object:
				return str(self.scryfall_object[field])
			else:
				return ""

		# Returns an error string if any part in the process throws an error.
		except Exception as E:
			print(f"Errant operation calculating field {field} for card {self.card_header}")
			print(E)
			return f"ERROR | {E}"


def read_blocks_from_sheet(filename):
	card_list = read_txt(filename)

	rarities = ["Commons", "Uncommons", "Rares", "Mythics", "Mythic Rares", "Lands"]
	last_rarity = "C"
	current_block_length = 0
	current_block = []
	all_blocks = []

	for line in card_list:
		if len(line) == 0:
			# print("New line!")
			if current_block_length > 0:
				new_card = {"rarity": last_rarity, "body": current_block}
				all_blocks.append(new_card)
				current_block = []
				current_block_length = 0
		else:
			# print(line)
			if line in rarities:
				print("Resetting Rarity!")
				last_rarity = line[0]
			else:
				current_block.append(line)
				current_block_length += 1

	return all_blocks


def create_cards_from_blocks(all_blocks):
	all_custom_cards = []

	for block in all_blocks:
		body = block["body"]
		is_reprint = find_regex_in_list(body, REGEX_REPRINT)
		if is_reprint > 0:
			new_custom_card = CustomCardReprint(body[0], body, block["rarity"])
			all_custom_cards.append(new_custom_card)
		elif len(body) > 2:
			new_custom_card = CustomCardSheet(body[0], body, block["rarity"])
			all_custom_cards.append(new_custom_card)

	return all_custom_cards


def process_fields_from_cards(all_custom_cards, output_fields):
	output_rows = []

	for custom_card in all_custom_cards:
		new_row = []
		for field in output_fields:
			new_row.append(custom_card.try_get_field(field))

		output_rows.append(new_row)

	return output_rows


def process_fields_from_cards_to_mse(all_custom_cards, output_fields):
	output_rows = []

	for custom_card in all_custom_cards:
		output_rows.append("card:")
		for field in output_fields:
			output_row = custom_card.try_get_field_mse(field)
			if len(output_row) > 0:
				output_rows.append(output_row)
		# print(output_row)
	# output_rows.append(new_row)

	return output_rows


def controller_import_custom_card_sheet(filename, output_fields):
	print(f"Importing from {filename}")
	all_blocks = read_blocks_from_sheet(filename)

	all_custom_cards = create_cards_from_blocks(all_blocks)
	output_rows = process_fields_from_cards(all_custom_cards, output_fields)

	output_rows.insert(0, output_fields)
	write_data_list(output_rows)


def controller_import_custom_card_sheet_to_mse(filename):
	print(f"Importing from {filename}")

	output_fields = ["name", "casting_cost", "super_type", "sub_type", "rarity", "rule_text", "power", "toughness",
	                 "flavor_text"]

	all_blocks = read_blocks_from_sheet(filename)

	all_custom_cards = create_cards_from_blocks(all_blocks)
	output_rows = process_fields_from_cards_to_mse(all_custom_cards, output_fields)

	# output_rows.insert(0, output_fields)
	write_data_to_txt(output_rows)


def find_regex_in_list(block, r):
	i = 0
	for line in block:
		m = r.fullmatch(line)
		if m is not None:
			return i
		else:
			i += 1
	return -1


if __name__ == '__main__':
	print("Importing and processing custom card sheet. V03")
	filename = "bin/baol.txt"
	output_fields = ["Name", "Set", "Slot", "Num", "Rarity", "Mana cost", "Color", "CMC", "type_line"]
	# output_fields = ["name"]

	# block = ["Yearning 5 my bestie", ":", "(Reprint)", "{T}: Add {C}.", "6/9","{P}"]
	# print(find_regex_in_list(block, REGEX_SYMBOL))

	controller_import_custom_card_sheet(filename, output_fields)
