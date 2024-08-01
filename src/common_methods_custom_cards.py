from common_methods_processor import get_color_code_from_colors


# Identifies all colors in card mana cost
def process_colors_from_mana_cost(mana_cost):
	all_colors = ["W", "U", "B", "R", "G", "C"]
	mana_cost = mana_cost.upper()
	card_colors = []

	for char in mana_cost:
		if char in all_colors and char not in card_colors:
			card_colors.append(char)

	return get_color_code_from_colors(card_colors)


# Processes mana value from a string mana cost. Returns an int
def process_mana_value_from_mana_cost(mana_cost):
	# all_colors = ["W", "U", "B", "R", "G", "C"]
	try:
		all_symbols = isolate_mana_symbols(mana_cost)
		mana_value = 0
		for symbol in all_symbols:
			# Splits symbol along any / character and takes the greatest values from between the sides.
			# This is necessary to handle hybrid mana symbols, written as {2/W}
			mana_characters = symbol.split("/")
			character_values = []
			for character in mana_characters:
				character_values.append(get_mana_value_from_symbol(character))
			mana_value += max(character_values)
		# mana_value += get_mana_value_from_symbol(symbol)

		return mana_value
	except Exception as E:
		print("Errant operation processing mana value!")
		print(E)
		return 0


# Gets the mana value from a given symbol
def get_mana_value_from_symbol(symbol):
	if symbol.isdigit():
		return int(symbol)
	else:
		return 1


# From a string mana cost, identifies each individual pip that makes up that cost
def isolate_mana_symbols(mana_cost):
	symbols = []
	is_inside_brackets = False
	this_brackets = ""

	# Identifies bracket delimited symbols
	for char in mana_cost:
		if is_inside_brackets:
			if char == "}":
				is_inside_brackets = False
				symbols.append(this_brackets)
			else:
				this_brackets += char
		else:
			if char == "{":
				is_inside_brackets = True
				this_brackets = ""
			else:
				symbols.append(char)

	# Combines any multi-character digits into a single character
	combined_digits = []
	is_digit = False
	this_digit = ""
	for symbol in symbols:
		if is_digit:
			if symbol.isdigit():
				this_digit += symbol
			else:
				combined_digits.append(this_digit)
				combined_digits.append(symbol)
				this_digit = ""
				is_digit = False
		else:
			if symbol.isdigit():
				this_digit = symbol
				is_digit = True
			else:
				combined_digits.append(symbol)

	if this_digit > "":
		combined_digits.append(this_digit)

	symbols = combined_digits

	return symbols


if __name__ == '__main__':
	print("Testing custom cards methods")
	print(process_mana_value_from_mana_cost("1U"))
	print(process_mana_value_from_mana_cost("0"))
	print(process_mana_value_from_mana_cost("10GG"))
	print(process_mana_value_from_mana_cost("{10}{G/R}{G/R}"))
	print(process_mana_value_from_mana_cost("{2/W}{2/U}{2/B}{2/R}{2/G}"))
