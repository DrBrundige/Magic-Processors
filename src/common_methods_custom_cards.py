from common_methods_processor import get_color_code_from_colors


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
