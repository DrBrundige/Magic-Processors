import os
import shared_methods_io


# Imports the latest full Scryfall download file containing each printing of each card.
def import_scryfall_full():
	path = get_latest_json("default-cards")
	print("Importing full Scryfall data at " + path)
	data = shared_methods_io.read_json("downloads/" + path)
	print(f"Success! Imported {len(data)} cards!")
	return data


# Imports the latest abridged Scryfall download file containing one printing for each unique card name.
def import_scryfall_abridged():
	path = get_latest_json("oracle-cards")
	print("Importing abridged Scryfall data at " + path)
	data = shared_methods_io.read_json("downloads/" + path)
	print(f"Success! Imported {len(data)} cards!")
	return data


# Imports the latest abridged Scryfall download file containing one printing for each unique card art.
def import_scryfall_art():
	path = get_latest_json("unique-artwork")
	print("Importing Scryfall unique art data at " + path)
	data = shared_methods_io.read_json("downloads/" + path)
	print(f"Success! Imported {len(data)} cards!")
	return data


def get_latest_json(json_class):
	all_files = os.listdir("downloads")
	all_files = [f for f in all_files if os.path.isfile("downloads" + '/' + f)]

	# Identifies all JSON files in downloads directory
	all_jsons = []
	for file in all_files:
		if file.endswith(".json"):
			all_jsons.append(file)

	all_timestamps = []
	for json in all_jsons:
		if json.startswith(json_class):
			try:
				all_timestamps.append(int(json[len(json_class) + 1:-5]))
			except Exception as E:
				print("Errant operation converting timestamp to int")
				print(E)

	if len(all_timestamps) == 0:
		print(f"Errant operation finding json for class {json_class}!"
		      f"No files with that name were found")
		return ""

	all_timestamps.sort(reverse=True)

	return f"{json_class}-{all_timestamps[0]}.json"


if __name__ == '__main__':
	print(get_latest_json("default-cards"))
