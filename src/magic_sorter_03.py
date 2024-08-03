from common_methods_io import read_json, read_csv, write_data, read_csv_get_headers
from common_methods_processor import format_cards_for_audit_sheet
# from magic_grinder_03 import *
from bulk_data_import import controller_get_sorted_data


class MagicSorterTrie03:
	# This dictionary contains instructions to sort each box.
	sorter_logic = {}
	# Each card is assigned to a box based on the home_box field. Each box has different criteria for sorting
	all_boxes = {}
	total_cards = 0

	def __init__(self, logic_file="sorter_logic.json", logic_json=None):
		# Reads the given json into the sorter_logic field
		if logic_json is None:
			self.sorter_logic = read_json(f"bin/{logic_file}")
		else:
			self.sorter_logic = logic_json
		self.all_boxes = {}
		self.reset_boxes()

	# Clears any existing boxes and creates new ones based on the sorter logic
	def reset_boxes(self):
		self.total_cards = 0
		self.all_boxes = {}
		for box in self.sorter_logic["all_box_names"]:
			new_box = BoxNode03(box, self.sorter_logic["box_logic"][box], self.sorter_logic["custom_sort_orders"])
			# print(new_box)
			self.all_boxes[box] = new_box

	def __str__(self):
		return f"Magic Sorter | Boxes: {len(self.all_boxes)}, Total cards: {self.total_cards}"

	# def add_sort_codes(self, card):
	# 	all_codes = self.sorter_logic["sort_codes"]
	# 	for key in all_codes.keys():
	# 		field = all_codes[key]["field"]
	# 		# print(card[field])
	# 		code = all_codes[key]["logic"][card.try_get_field(field)]
	# 		card.sort_codes[key] = code

	# Adds a card to a box using the recursive BoxNode.add_card method
	def add_card(self, card):
		matching_box = card.try_get_field("home_box")
		# self.add_sort_codes(card)
		self.all_boxes[matching_box].add_card(card)
		self.total_cards += 1

	def output_cards(self):
		all_cards = []
		for box in self.all_boxes.values():
			box_cards = []
			box.output_branch_cards(box_cards)
			for card in box_cards:
				all_cards.append(card)
		return all_cards


class BoxNode03:
	name = ""
	logic = None
	# I'm not sure whether its OK for a subclass to have a reference to its parent.
	#   In any case, each BoxNode has a reference to the custom_sort_orders logic
	custom_sort_orders = {}

	contains_cards = False
	all_sub_nodes = {}
	all_cards = []

	def __init__(self, name, logic, custom_sort_orders):
		self.all_sub_nodes = {}
		self.all_cards = []
		self.name = name
		self.logic = []

		for logic_item in logic:
			if type(logic_item) == str:
				self.logic.append(Logic03(logic_item))
			else:
				self.logic.append(logic_item)

		self.custom_sort_orders = custom_sort_orders
		if len(logic) == 0:
			self.contains_cards = True

	def __copy__(self):
		new_box = BoxNode03(self.name, self.logic, self.custom_sort_orders)
		return new_box

	def __str__(self):
		return f"{self.name}"

	def add_card(self, card):
		if self.contains_cards and len(self.logic) == 0:
			self.all_cards.append(card)
			return True
		else:
			# next_node_name = card[self.logic[0].lower()]
			next_node_name = card.try_get_field(self.logic[0].name)
			if next_node_name not in self.all_sub_nodes:
				new_logic = self.logic[1:len(self.logic)]
				new_node = BoxNode03(next_node_name, new_logic, self.custom_sort_orders)

				self.all_sub_nodes[next_node_name] = new_node

			return self.all_sub_nodes[next_node_name].add_card(card)

	# Takes all cards in the trie and outputs them in order
	def output_branch_cards(self, box_cards):
		# If this branch contains cards, we have reached the end of the sort logic chain
		# The cards will be added. Usually, only one card will be added per branch, but there may be more
		if self.contains_cards:
			for card in self.all_cards:
				box_cards.append(card)
			return True
		else:
			# Sorts the sub boxes in the current box and recurses through each
			sorted_keys = []
			this_logic = self.logic[0]
			logic_tags = this_logic.tags

			# Sorts by integer value instead of string
			if this_logic in self.custom_sort_orders:
				custom_sort_order = self.custom_sort_orders[this_logic]

				# Iterates through the custom order. If it finds a matching key, adds it to the sorted_keys list
				for custom_sort in custom_sort_order:
					if custom_sort in self.all_sub_nodes:
						sorted_keys.append(custom_sort)

				# This shouldn't ever get used, but in case there are any keys not in the sort logic,
				#   they will be added be added here.
				for key in self.all_sub_nodes.keys():
					if key not in sorted_keys:
						sorted_keys.append(key)
			else:
				# The 'standard' method of sorting keys. Adds each key to a list and sorts alphabetically
				for key in self.all_sub_nodes.keys():
					sorted_keys.append(key)
				sorted_keys.sort()

			# Applies special tags, even though some of these tags completely overrides previous sort logic lol
			if "ints" in logic_tags:
				sorted_keys = []
				sorted_keys_ints = []
				sorted_keys_strs = []

				for key in self.all_sub_nodes.keys():
					if key.isdigit():
						sorted_keys_ints.append(int(key))
					else:
						sorted_keys_strs.append(key)

				sorted_keys_ints.sort()
				sorted_keys_strs.sort()

				for sorted_int in sorted_keys_ints:
					sorted_keys.append(str(sorted_int))

				for sorted_str in sorted_keys_strs:
					sorted_keys.append(sorted_str)

			if "reverse" in logic_tags:
				sorted_keys.reverse()

			# Categories such as color_id and card_type get special logic.
			#   The sorter_logic contains a custom order that this algorith attempts to replicate

			# Recurses through each box in the sorted order
			for sorted_key in sorted_keys:
				self.all_sub_nodes[sorted_key].output_branch_cards(box_cards)


class Logic03:
	name = ""
	tags = []
	name_str = ""
	has_tags = False

	def __init__(self, name_str):
		self.name_str = name_str
		split_name = name_str.split("|")
		self.name = split_name.pop(0).lower()
		self.tags = split_name
		self.has_tags = len(self.tags) > 0

	def __str__(self):
		return self.name_str


def controller_test_sorter():
	SortAudit = MagicSorterTrie03("sorter_logic_03.json")


if __name__ == '__main__':
	print("Sorting cards!")
	controller_test_sorter()
