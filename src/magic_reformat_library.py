import datetime

import cool_stuff


def do_reformat(card_names):
	source_cards = cool_stuff.read_csv(card_names)

	formatted_cards = reformat_library_to_audit(source_cards)

	cool_stuff.write_data(formatted_cards)


# For a library dataset, reformats as audit.
def reformat_library_to_audit(source_cards):
	audit = []
	all_audit_columns = (
		"Is Foil", "Variant", "Special Art", "C. No.", "Set", "Home Box", "Section")

	for card in source_cards:
		new_card = {'Name': card['Name']}
		for column in all_audit_columns:
			if column in card:
				new_card[column] = card[column]

		new_card["Year"] = datetime.date.today().year

		for i in range(int(card['Qt'])):
			audit.append(new_card.copy())

	return audit


if __name__ == '__main__':
	print("Reformat Library")
	do_reformat("all_order_test_cards.csv")
