import re

from common_methods_io import read_txt, write_data
from common_methods_grinder import get_color_code_from_colors
from import_scryfall_bulk_data import import_scryfall_abridged

REGEX_REPRINT = re.compile("\(Reprint\)")  # Validates that the string is the word (Reprint)
REGEX_PT = re.compile("(^.{1,2}/.{1,2}$)")  # Validates that the string is power / toughness
REGEX_FLAVOR = re.compile("(^-{4,9}$)")  # Validates that the string is the underbar separating rules from flavor text
REGEX_COLOR = re.compile("(^\(.*\)$)")
REGEX_SYMBOL = re.compile("(^\{.*\}$)")

class CustomCard:
	card_header = ""
	block = [""]
	rarity = ""

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
				return body

			elif field == "name":
				return self.try_get_name()
			elif field == "type_line":
				return self.try_get_type_line()
			elif field == "rarity":
				return self.try_get_rarity()
			elif field == "mana_cost":
				return self.try_get_mana_cost()
			else:
				return ""

		# Returns an error string if any part in the process throws an error.
		except Exception as E:
			print(f"Errant operation calculating field {field} for card {self.card_header}")
			print(E)
			return f"ERROR | {E}"

	# Perhaps some day I can start putting the correct notation for mana in the cost section but I'm too lazy right now
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

	def try_get_rarity(self):
		split_type = self.block[1].split("|")
		if len(split_type) > 1:
			return str.strip(split_type[1])[0]
		else:
			return self.rarity

	def try_get_type_line(self):
		split_type = self.block[1].split("|")

		return str.strip(split_type[0])


def read_blocks_from_sheet(filename):
	card_list = read_txt(filename)

	rarities = ["Commons", "Uncommons", "Rares", "Mythics", "Mythic Rares"]
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
			print("Card is reprint! I'll deal with this later")
		elif len(body) > 2:
			new_custom_card = CustomCard(body[0], body, block["rarity"])
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


def controller_import_custom_card_sheet(filename, output_fields):
	print(f"Importing from {filename}")
	all_blocks = read_blocks_from_sheet(filename)

	all_custom_cards = create_cards_from_blocks(all_blocks)
	output_rows = process_fields_from_cards(all_custom_cards, output_fields)

	return output_rows


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
	output_fields = ["name", "mana_cost"]

	# block = ["Yearning 5 my bestie", ":", "(Reprint)", "{T}: Add {C}.", "6/9","{P}"]
	# print(find_regex_in_list(block, REGEX_SYMBOL))

	all_rows = controller_import_custom_card_sheet(filename, output_fields)

	for row in all_rows:
		print(row)
