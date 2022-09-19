import requests
import json
import base64


def call_scryfall_creature_types():
	r = requests.get('https://api.scryfall.com/catalog/creature-types')

	if r.status_code == 200:
		data = r.json()
		# print(data)
		print(data['object'])
		print(data['data'])
		return data['data']
	else:
		print('Request failed, error code: ' + str(r.status_code) + ' | ' + r.reason)
		return False


if __name__ == '__main__':
	print("Calling Scryfall API")
	call_scryfall_creature_types()
