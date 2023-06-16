from shared_methods_io import read_json, read_csv, write_data
from magic_grinder_02_match_data import match_bulk_data, controller_get_sorted_data
from magic_grinder_02_match_data_processors import get_audit_row
from magic_grinder_02_match_data_match_methods import standard_match_full


class MagicSorterTrie:
	sorter_logic = {}
	all_boxes = {}
	total_cards = 0

	def __init__(self, logic_file="sorter_logic.json"):
		self.sorter_logic = read_json(f"bin/{logic_file}")
		self.all_boxes = {}
		self.reset_boxes()

	def reset_boxes(self):
		self.total_cards = 0
		self.all_boxes = {}
		for box in self.sorter_logic["all_box_names"]:
			new_box = BoxNode(box, self.sorter_logic["box_logic"][box])
			# print(new_box)
			self.all_boxes[box] = new_box

	def __str__(self):
		return f"Magic Sorter | Boxes: {len(self.all_boxes)}, Total cards: {self.total_cards}"

	def add_card(self, card):
		matching_box = card["home_box"]
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


# Because this algorithm is intended to read directly from the audit sheet, it expects column names to be
#    uncapitalized with spaces
# Name,ID,New ID,Set,Set No,Is Foil,Home Box,Section,Card Type
if __name__ == '__main__':
	print("Sorting card collection")
	SortAudit = MagicSorterTrie("sorter_logic.json")

	all_cards = read_csv("audit_csv.csv", do_snake_case_names=True, do_standardize_header_names=True)
	all_sort_cards = match_bulk_data(controller_get_sorted_data(), all_cards, standard_match_full, get_audit_row,
	                                 do_output_count=False)

	for card in all_sort_cards:
		print(f"Sorting card {card['name']}")
		SortAudit.add_card(card)

	# print(SortAudit)
	all_sorted_cards = SortAudit.output_cards()
	print(len(all_sorted_cards))
	new_id = 1
	for card in all_sorted_cards:
		card["new id"] = new_id
		new_id += 1
	write_data(all_sorted_cards, "reorder")

# print(SortAudit.sorter_logic)
