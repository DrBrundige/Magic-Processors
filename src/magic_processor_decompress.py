from common_methods_io import read_csv, write_data, snake_case_parameter


# I don't know if I ever wrote a dedicated method for this process, but if I did, I can't find it.
# In any case, takes a sheet with a count row and returns that same sheet with each row
#     duplicated a number of times for the value of count (Converts a set sheet to an audit sheet.)
def decompress_set_sheet(all_rows, count_col):
	all_decompressed_rows = []
	for row in all_rows:
		try:
			if row[count_col].isdigit():
				r = range(int(row[count_col]))
				for x in r:
					all_decompressed_rows.append(row)
		except Exception as E:
			pass

	return all_decompressed_rows


def controller_decompress_set_sheet(filename, count_col):
	all_rows = read_csv(filename, True, True)

	all_decompressed_rows = decompress_set_sheet(all_rows, snake_case_parameter(count_col))

	write_data(all_decompressed_rows)


if __name__ == '__main__':
	print("Decompressing Rows")
	filename = "all_order_cards.csv"
	controller_decompress_set_sheet(filename, "Count")
