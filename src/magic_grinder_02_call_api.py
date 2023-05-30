import requests
from shared_methods_io import write_data
# Don't get me wrong - my search methods work,
# but sometimes it's best to get data straight from the source.


# Attempts to contact the Scryfall API.
#   This method uses no access token, so only basic information may be retrieved.
#   Nevertheless, this includes a wide range of data
# Returns data payload as list of strings on success. Returns None on fail
def call_scryfall(endpoint):
	try:
		print("Contacting Scryfall API")
		r = requests.get(f'https://api.scryfall.com/{endpoint}')

		if r.status_code == 200:
			data = r.json()
			print(f"Success! Returned {len(data['data'])} rows")
			# print(data)
			# print(data['object'])
			# print(data['data'])
			return data['data']
		else:
			print('Request failed, error code: ' + str(r.status_code) + ' | ' + r.reason)
			return None
	except Exception as E:
		print("Error contacting Scryfall!")
		print(E)
		return None


# Calls Scryfall API and attempts to parse information
# Searches each return row for parameterized strings and returns those fields as a list of strings
# Returns data on success.
def parse_scryfall_data(endpoint, fields):
	data = call_scryfall(endpoint)
	new_rows = []
	for scryfall_object in data:
		new_row = {}
		for field in fields:
			if field in scryfall_object:
				new_row[field] = scryfall_object[field]
			else:
				new_row[field] = ""
		new_rows.append(new_row)

	return new_rows


# Controller. Calls parse_scryfall_data() to retrieve information on all sets and prints
def controller_get_set_data():
	fields = ["code", "name", "released_at"]
	set_data = parse_scryfall_data("sets", fields)
	write_data(set_data, "sets")


# Controller. Calls call_scryfall() to retrieve each creature type and returns as list of strings
def controller_get_scryfall_creature_types():
	# r = requests.get('https://api.scryfall.com/catalog/creature-types')
	return call_scryfall("catalog/creature-types")


if __name__ == '__main__':
	print("Calling Scryfall API")
	# call_scryfall("bingus")
	print(controller_get_scryfall_creature_types())
	# controller_get_set_data()
