from common_methods_io import read_txt, write_data
from common_methods_grinder import get_color_code_from_colors
from import_scryfall_bulk_data import import_scryfall_abridged


def read_blocks_from_sheet(filename):
	card_list = read_txt(filename)

	rarities = ["Commons", "Uncommons", "Rares"]
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


def process_cards_from_blocks(all_blocks):
	all_cards = []
	scryfall_data = import_scryfall_abridged()

	# This is an extremely rigid way of handling this logic.
	#     Perhaps someday I can rework it like the grinder v03 to handle a given list of parameters,
	#     but it works for now
	for block in all_blocks:
		body = block["body"]
		name = body[0]

		try:
			# print(name)
			is_reprint = False
			for line in block["body"]:
				if line == "(Reprint)":
					is_reprint = True

			if is_reprint:
				name = block["body"].pop(0)
				# I almost always include the mana cost after the name of a reprint card. This checks both.
				matched_card = next(
					(item for item in scryfall_data if (item['name'].lower()) == name.lower()), None)

				if matched_card is None:
					# print("Found card!")
					split_name = name.split()
					split_name.pop(-1)
					name_without_mana = " ".join(split_name)
					matched_card = next(
						(item for item in scryfall_data if (item['name'].lower()) == name_without_mana.lower()), None)
					if matched_card is None:
						print(f"Errant operation! Could not find card {name}")
						continue

				# Assigns rarity to the previous value. Sorry?
				this_card = {"name": matched_card["name"], "mana_cost": matched_card["mana_cost"],
				             "color": get_color_code_from_colors(matched_card["colors"]), "cmc": matched_card["cmc"],
				             "type_line": matched_card["type_line"], "rarity": block["rarity"],
				             "rules": ""}
				rules = matched_card["oracle_text"]

				for extra_rules in block["body"]:
					rules += f"\n{extra_rules}"
				this_card["rules"] = rules
				all_cards.append(this_card)

			else:
				this_card = {"name": "", "mana_cost": "", "color": "", "cmc": "", "type_line": "", "rarity": "",
				             "rules": ""}
				if len(block["body"]) < 3:
					# print(f"'Card' ({name}) contains too few lines!")
					continue
				else:
					# Processes name, mana cost, and colors from first line
					first_line = block["body"].pop(0).split()
					mana_cost = first_line.pop(len(first_line) - 1)
					# print(mana_cost)

					# Remember how I said that the logic will consider a mana cost enclosed in parentheses to have
					#     no casting cost? That was a lie. It checks only the open paren lmao I'm too lazy.
					if mana_cost[0] != "(":
						this_card["mana_cost"] = mana_cost
					this_card["color"] = process_colors_from_mana_cost(mana_cost)
					this_card["cmc"] = process_mana_value_from_mana_cost(mana_cost)
					joined_name = " ".join(first_line)
					this_card["name"] = joined_name

					# Processes type line and rarity from second line
					second_line = block["body"].pop(0).split("|")
					this_card["type_line"] = second_line[0].strip()
					if len(second_line) > 1:
						# This rather ugly line assigns the first character after being stripped
						this_card["rarity"] = second_line[1].strip()[0]
					else:
						this_card["rarity"] = block["rarity"]
					# print(second_line)

					rules = block["body"].pop(0)

					for extra_rules in block["body"]:
						rules += f"\n{extra_rules}"

					this_card["rules"] = rules
					# print(this_card)
					all_cards.append(this_card)

		except Exception as E:
			print("Errant operation processing card! Skipping card")
			print(name)
			print(E)

	return all_cards


def process_colors_from_mana_cost(mana_cost):
	all_colors = ["W", "U", "B", "R", "G", "C"]
	mana_cost = mana_cost.upper()
	card_colors = []

	for char in mana_cost:
		if char in all_colors and char not in card_colors:
			card_colors.append(char)

	return get_color_code_from_colors(card_colors)


# An extremely lazy way of calculating mana value. Does not take into account split or hybrid mana
# TODO: This doesn't work with lands. I'm not sure if it's the fault of this method or the logic that invokes it.
def process_mana_value_from_mana_cost(mana_cost):
	all_colors = ["W", "U", "B", "R", "G", "C"]
	colors = 0
	generic = ""

	for char in mana_cost:
		if char in all_colors:
			colors += 1
		elif char.isdigit():
			generic += char

	mana_value = colors
	if len(generic) > 0:
		mana_value += int(generic)
	return mana_value


def controller_import_custom_card_sheet(filename):
	print(f"Importing from {filename}")
	all_blocks = read_blocks_from_sheet(filename)
	all_cards = process_cards_from_blocks(all_blocks)
	return all_cards


if __name__ == '__main__':
	print("Importing and processing custom card sheet.")
	all_cards = controller_import_custom_card_sheet("bin/baol.txt")
	write_data(all_cards)
