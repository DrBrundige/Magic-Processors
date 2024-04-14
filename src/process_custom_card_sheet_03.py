import re

from common_methods_io import read_txt, write_data, write_data_list, write_data_to_txt, snake_case_parameter_list
from common_methods_call_scryfall import call_scryfall_03
from common_methods_processor import get_color_code_from_colors, get_card_type_from_type_line
# from import_scryfall_bulk_data import import_scryfall_abridged
from common_methods_custom_cards import process_colors_from_mana_cost, process_mana_value_from_mana_cost

REGEX_REPRINT = re.compile("\(Reprint\)")  # Validates that the string is the word (Reprint)
REGEX_PT = re.compile("(^.{1,2}/.{1,2}$)")  # Validates that the string is power / toughness
REGEX_FLAVOR = re.compile("(^-{4,9}$)")  # Validates that the string is the underbar separating rules from flavor text
REGEX_COLOR = re.compile("(^\(.*\)$)")
REGEX_SYMBOL = re.compile("(^\{.*\}$)")


class CustomCard:
	# The card name
	name = ""
	slot = "0"
	set_code = ""

	# All potential rarities. Used for MSE shit
	rarities = {"C": "common", "U": "uncommon", "R": "rare", "M": "mythic rare", "L": "land"}

	def __init__(self, name, slot=0, set_code=""):
		self.name = name
		self.slot = str(slot)
		self.set_code = set_code

	def __str__(self):
		return self.name

	# Tries to return a field of the given name
	def try_get_field(self, field):
		try:
			if field == "name":
				return self.name
			if field == "slot":
				return self.slot
			if field == "set":
				return self.set_code
			else:
				return ""
		# Returns an error string if any part in the process throws an error.
		except Exception as E:
			print(f"Errant operation calculating field {field} for card {self.name}")
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
			# return_string = " ".join(self.try_get_field("flavor"))
			return_string = self.try_get_field("flavor")

		if len(return_string) > 0:
			return f"\t{field}: {return_string}"
		else:
			return ""


class CustomCardText(CustomCard):
	# A representation of a text-based description of a card.
	# The first line of the card, containing name and mana cost
	card_header = ""
	# Each text line of the card as a list of strings
	block = [""]
	# Because the rarity is not printed on each card, stores the rarity here.
	# If the rarity is printed, that rarity wins.
	rarity = ""

	def __init__(self, card_header, block, rarity, slot=0, set_code=""):
		self.card_header = card_header
		self.block = block
		self.rarity = rarity
		name = self.try_get_name_from_header()
		super().__init__(name, slot, set_code)

	def try_get_field(self, field):
		try:
			return_text = super().try_get_field(field=field)
			if len(return_text) > 0:
				return return_text

			elif field == "header":
				return self.card_header
			elif field == "card_body":
				body = self.block.copy()
				body.pop(0)
				body.pop(0)
				return "\n".join(body)
			elif field == "type_line":
				return self.try_get_type_line()
			elif field == "type":
				return get_card_type_from_type_line(self.try_get_type_line())
			elif field == "rarity":
				return self.try_get_rarity()
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
			elif field == "flavor":
				return " ".join(self.try_get_flavor())
			else:
				return ""

		# Returns an error string if any part in the process throws an error.
		except Exception as E:
			print(f"Errant operation calculating field {field} for card {self.name}")
			print(E)
			return f"ERROR | {E}"

	# Perhaps some day I can start putting the correct notation for mana in the cost section, but I'm too lazy right now
	def try_get_name_from_header(self):
		split_name = self.card_header.split()
		split_name.pop(-1)
		name_without_mana = " ".join(split_name)
		return name_without_mana

	# Tries to get the mana cost, which should be the last word of the first line.
	def try_get_mana_cost(self):
		split_name = self.card_header.split()
		cost = split_name.pop()

		m = REGEX_COLOR.fullmatch(cost)
		if m is not None:
			return ""
		else:
			return cost

	# Tries to get the CMC, derived from the mana cost
	def try_get_cmc(self):
		return str(process_mana_value_from_mana_cost(self.try_get_mana_cost()))

	# Tries to get the type line, which should be the second line of the block
	def try_get_type_line(self):
		split_type = self.block[1].split("|")

		return str.strip(split_type[0])

	# Tries to get the color which as far as this logic can tell, is derived from the mana cost
	def try_get_color(self):
		return process_colors_from_mana_cost(self.try_get_mana_cost())

	# Tries to get the rules text, which should be between the type line and either the PT or a bar
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

	# Tries to get the power / toughness, which should be two digits separated by a slash
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

	# Tries to get the flavor text, which is any text after four dashes "----"
	def try_get_flavor(self):
		flavor_row = find_regex_in_list(self.block, REGEX_FLAVOR)
		if flavor_row > -1:
			return self.block[flavor_row + 1:len(self.block)]
		else:
			return ""

	# Tries to get the printed rarity if any exists. Otherwise returns the default
	def try_get_rarity(self):
		split_type = self.block[1].split("|")
		if len(split_type) > 1:
			return str.strip(split_type[1])[0]
		else:
			return self.rarity


class CustomCardReprint(CustomCardText):
	scryfall_object = {}

	def __init__(self, card_header, block, rarity, slot=0, set_code=""):
		super().__init__(card_header, block, rarity, slot, set_code)
		self.try_get_card_from_scryfall()

	# Retrieves a card with the same name from the Scryfall API.
	# I assumed this would be faster than importing the full bulk data, but I forgot how many reprints I have in my set.
	def try_get_card_from_scryfall(self):
		split_name = self.name.split()
		# split_name.pop(-1)
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
			if field == "rules":
				return self.scryfall_object["oracle_text"]
			elif field == "color" or field == "color_identity":
				return get_color_code_from_colors(self.scryfall_object["color_identity"])
			elif field == "rarity":
				return self.try_get_rarity()
			if field == "set":
				return self.set_code
			elif field in self.scryfall_object:
				return str(self.scryfall_object[field])
			else:
				return super().try_get_field(field=field)

		# Returns an error string if any part in the process throws an error.
		except Exception as E:
			print(f"Errant operation calculating field {field} for card {self.name}")
			print(E)
			return f"ERROR | {E}"

	def try_get_type_line(self):
		return self.scryfall_object["type_line"]

# class CustomCardSpreadsheet(CustomCard):
# 	card_object = {}
#
# 	def __init__(self, card_header, block, rarity):
# 		super().__init__(card_header, block, rarity)


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

	if current_block_length > 0:
		new_card = {"rarity": last_rarity, "body": current_block}
		all_blocks.append(new_card)

	return all_blocks


def create_cards_from_blocks(all_blocks, set_code=""):
	all_custom_cards = []

	slot = 1

	for block in all_blocks:
		body = block["body"]
		is_reprint = find_regex_in_list(body, REGEX_REPRINT)
		if is_reprint > 0:
			new_custom_card = CustomCardReprint(body[0], body, block["rarity"], slot=slot, set_code=set_code)
			all_custom_cards.append(new_custom_card)
			slot += 1
		elif len(body) > 2:
			new_custom_card = CustomCardText(body[0], body, block["rarity"], slot=slot, set_code=set_code)
			all_custom_cards.append(new_custom_card)
			slot += 1

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


def controller_import_custom_card_sheet(filename, output_fields, set_code=""):
	print(f"Importing from {filename}")
	all_blocks = read_blocks_from_sheet(filename)

	output_fields = snake_case_parameter_list(output_fields)

	all_custom_cards = create_cards_from_blocks(all_blocks, set_code=set_code)
	output_rows = process_fields_from_cards(all_custom_cards, output_fields)

	if len(output_rows) > 0:
		output_rows.insert(0, output_fields)
		write_data_list(output_rows)
	else:
		print("Errant operation! No cards output")


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
	# output_fields = ["Slot", "Name", "mana cost", "Color", "CMC", "Type", "Rarity", "Rules", "Power", "Toughness"]

	# Output for Card Type Breakdowns sheet
	output_fields = ["Name", "Set", "Slot", "Rarity", "Mana cost", "Color", "CMC", "Type"]
	# output_fields = ["name"]

	# block = ["Yearning 5 my bestie", ":", "(Reprint)", "{T}: Add {C}.", "6/9","{P}"]
	# print(find_regex_in_list(block, REGEX_SYMBOL))

	# controller_import_custom_card_sheet_to_mse(filename)
	controller_import_custom_card_sheet(filename, output_fields, set_code="BRY")
