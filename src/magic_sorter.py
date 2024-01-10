from shared_methods_io import read_json, read_csv, write_data, read_csv_get_headers
from magic_grinder_02_match_data import match_bulk_data, controller_get_sorted_data
from magic_grinder_02_match_data_processors import get_audit_row
from magic_grinder_02_match_data_match_methods import standard_match_full
from shared_methods_grinder import format_cards_for_audit_sheet
# from magic_grinder_03 import match_cards_03


# TODO: Add an error box that gets generated automatically.
#    Cards that throw errors in the add_card stage are assigned here
#    On output_cards, they are output at the end and not assigned a new_id


# Man, I'm glad this shit works because if anything breaks on it,
#     I do NOT remember enough about how it functions to fix it.
class MagicSorterTrie:
	# This dictionary contains instructions to sort each box.
	sorter_logic = {}
	# Each card is assigned to a box based on the home_box field. Each box has different criteria for sorting
	all_boxes = {}
	total_cards = 0

	def __init__(self, logic_file="sorter_logic.json"):
		# Reads the given json into the sorter_logic field
		self.sorter_logic = read_json(f"bin/{logic_file}")
		self.all_boxes = {}
		self.reset_boxes()

	# Clears any existing boxes and creates new ones based on the sorter logic
	def reset_boxes(self):
		self.total_cards = 0
		self.all_boxes = {}
		for box in self.sorter_logic["all_box_names"]:
			new_box = BoxNode(box, self.sorter_logic["box_logic"][box])
			# print(new_box)
			self.all_boxes[box] = new_box

	def __str__(self):
		return f"Magic Sorter | Boxes: {len(self.all_boxes)}, Total cards: {self.total_cards}"

	# Matches the keys in the sorter_logic["sort_codes"] against the keys in the given card
	# Adds the results to new keys in the card dictionary
	def add_sort_codes(self, card):
		all_codes = self.sorter_logic["sort_codes"]
		for key in all_codes.keys():
			field = all_codes[key]["field"]
			# print(card[field])
			code = all_codes[key]["logic"][card[field]]
			card[key] = code

	# Adds a card to a box using the recursive BoxNode.add_card method
	def add_card(self, card):
		matching_box = card["home_box"]
		self.add_sort_codes(card)
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


class BoxNode:
	name = ""
	logic = []

	contains_cards = False
	all_sub_nodes = {}
	all_cards = []

	def __init__(self, name, logic):
		self.all_sub_nodes = {}
		self.all_cards = []
		self.name = name
		self.logic = logic
		if len(logic) == 0:
			self.contains_cards = True

	def __str__(self):
		return f"{self.name}"

	def add_card(self, card):
		# If the list of logic is empty, adds card.
		# Otherwise, creates a new node with the bottom element of the logic list removed. Recurses
		if self.contains_cards and len(self.logic) == 0:
			self.all_cards.append(card)
			return True
		else:
			next_node_name = card[self.logic[0].lower()]
			if next_node_name not in self.all_sub_nodes:
				new_logic = self.logic[1:len(self.logic)]
				new_node = BoxNode(next_node_name, new_logic)

				self.all_sub_nodes[next_node_name] = new_node

			return self.all_sub_nodes[next_node_name].add_card(card)

	def output_branch_cards(self, box_cards):
		if self.contains_cards:
			for card in self.all_cards:
				box_cards.append(card)
			return True
		else:
			sorted_keys = []

			if self.logic[0].lower() == "collector_number":
				for key in self.all_sub_nodes.keys():
					sorted_keys.append(int(key))
				sorted_keys.sort()
				for sorted_key in sorted_keys:
					self.all_sub_nodes[str(sorted_key)].output_branch_cards(box_cards)
			else:
				for key in self.all_sub_nodes.keys():
					sorted_keys.append(key)
				sorted_keys.sort()
				for sorted_key in sorted_keys:
					self.all_sub_nodes[sorted_key].output_branch_cards(box_cards)


# Processes the given cards using the magic_grinder_02 and sorts
def controller_sort_02(sort_logic="sorter_logic.json", filename="audit_csv.csv"):
	SortAudit = MagicSorterTrie(sort_logic)

	all_cards = read_csv(filename, do_snake_case_names=True, do_standardize_header_names=True)
	all_sort_cards = match_bulk_data(controller_get_sorted_data(), all_cards, standard_match_full, get_audit_row,
	                                 do_output_count=False)

	for card in all_sort_cards:
		# print(f"Sorting card {card['name']}")
		SortAudit.add_card(card)

	# print(SortAudit)
	all_sorted_cards = SortAudit.output_cards()
	print(len(all_sorted_cards))
	new_id = 1
	for card in all_sorted_cards:
		card["id"] = new_id
		new_id += 1

	format_cards_for_audit_sheet(all_sorted_cards)
	write_data(all_sorted_cards, "reorder")


# Because this algorithm is intended to read directly from the audit sheet, it expects column names to be
#    uncapitalized with spaces
# Name,ID,New ID,Set,Set No,Is Foil,Home Box,Section,Card Type
if __name__ == '__main__':
	print("Sorting card collection")
	controller_sort_02()
