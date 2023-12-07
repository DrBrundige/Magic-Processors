from shared_methods_io import read_json, read_csv, write_data, read_csv_get_headers
from shared_methods_grinder import format_cards_for_audit_sheet
from magic_grinder_03 import *
from import_scryfall_bulk_data import controller_get_sorted_data


class MagicSorterTrie03:
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
			new_box = BoxNode03(box, self.sorter_logic["box_logic"][box])
			# print(new_box)
			self.all_boxes[box] = new_box

	def __str__(self):
		return f"Magic Sorter | Boxes: {len(self.all_boxes)}, Total cards: {self.total_cards}"

	def add_sort_codes(self, card):
		all_codes = self.sorter_logic["sort_codes"]
		for key in all_codes.keys():
			field = all_codes[key]["field"]
			# print(card[field])
			code = all_codes[key]["logic"][card.try_get_field(field)]
			card.sort_codes[key] = code

	# Adds a card to a box using the recursive BoxNode.add_card method
	def add_card(self, card):
		matching_box = card.try_get_field("home_box")
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


class BoxNode03:
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
		if self.contains_cards and len(self.logic) == 0:
			self.all_cards.append(card)
			return True
		else:
			next_node_name = card[self.logic[0].lower()]
			if next_node_name not in self.all_sub_nodes:
				new_logic = self.logic[1:len(self.logic)]
				new_node = BoxNode03(next_node_name, new_logic)

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


def controller_sort_03(data, sort_logic="sorter_logic.json", filename="audit_csv.csv"):
	SortAudit = MagicSorterTrie03(sort_logic)
	# Import cards from filename
	all_cards = read_csv(filename, True, True)
	all_new_cards = []

	# Create NewCard objects for each card
	for card in all_cards:
		this_card = NewCard(card)

		if this_card.try_match_self(data):
			all_new_cards.append(this_card)


# Sort NewCard objects with MagicSorterTrie03 (it has been reworked to accept NewCard objects
# Process cards in the manner of magic_grinder_03 (may have to move rearrange code to make it more modular)
# Output, being sure that the original headers are maintained


if __name__ == '__main__':
	print("Sorting cards!")
	data = controller_get_sorted_data(path="test-cards")

	controller_sort_03(data=data)
