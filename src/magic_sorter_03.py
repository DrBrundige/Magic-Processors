from shared_methods_io import read_json, read_csv, write_data, read_csv_get_headers
from shared_methods_grinder import format_cards_for_audit_sheet
# from magic_grinder_03 import *
from import_scryfall_bulk_data import controller_get_sorted_data


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
	logic = []
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
		self.logic = logic
		self.custom_sort_orders = custom_sort_orders
		if len(logic) == 0:
			self.contains_cards = True

	def __str__(self):
		return f"{self.name}"

	def add_card(self, card):
		if self.contains_cards and len(self.logic) == 0:
			self.all_cards.append(card)
			return True
		else:
			# next_node_name = card[self.logic[0].lower()]
			next_node_name = card.try_get_field(self.logic[0].lower())
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

			# Collector number gets special logic to sort by integer value.
			# In the future, I may make this smarter, but it's fine for this purpose
			if this_logic == "collector_number":
				sorted_keys_ints = []
				for key in self.all_sub_nodes.keys():
					sorted_keys_ints.append(int(key))
				sorted_keys_ints.sort()
				for sorted_int in sorted_keys_ints:
					sorted_keys.append(str(sorted_int))

			# Categories such as color_id and card_type get special logic.
			#   The sorter_logic contains a custom order that this algorith attempts to replicate
			elif this_logic in self.custom_sort_orders:
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

			# Recurses through each box in the sorted order
			for sorted_key in sorted_keys:
				self.all_sub_nodes[sorted_key].output_branch_cards(box_cards)


#
# # Using the MagicSorterTrie and NewCard class, sorts each card from the given file, processes, and prints
# def controller_sort_03(data, sort_logic="sorter_logic_03.json", filename="audit_csv.csv"):
# 	SortAudit = MagicSorterTrie03(sort_logic)
# 	# Import cards from filename
# 	all_cards = read_csv(filename, True, True)
# 	audit_rows = []
#
# 	# Create NewCard objects for each card
# 	for card in all_cards:
# 		this_card = NewCard(card)
#
# 		if this_card.try_match_self(data):
# 			SortAudit.add_card(this_card)
# 	# all_new_cards.append(this_card)
#
# 	all_sorted_cards = SortAudit.output_cards()
#
# 	match_fields = read_csv_get_headers(name=filename, do_standardize_header_names=True,
# 	                                    do_snake_case_names=True)
# 	audit_rows.append(read_csv_get_headers(name=filename))
#
# 	i = 1
# 	for this_card in all_sorted_cards:
# 		new_row = []
# 		this_card.sorter_id = i
# 		for match_field in match_fields:
# 			new_row.append(this_card.try_get_field(match_field))
#
# 		audit_rows.append(new_row)
# 		i += 1
#
# 	write_data_list(audit_rows, "sorted")
#

# Sort NewCard objects with MagicSorterTrie03 (it has been reworked to accept NewCard objects
# Process cards in the manner of magic_grinder_03 (may have to move rearrange code to make it more modular)
# Output, being sure that the original headers are maintained


if __name__ == '__main__':
	print("Sorting cards!")
	data = controller_get_sorted_data(path="test-cards")

# controller_sort_03(data=data)
