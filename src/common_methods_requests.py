import shutil
import time

from datetime import datetime, timedelta

import requests


# from shared_methods_io import write_data


# Don't get me wrong - my search methods work,
# but sometimes it's best to get data straight from the source.
# Call API 02 hasn't gone anywhere and still works, but I thought I'd take this opportunity to fix some slight issues


# Attempts to contact the Scryfall API.
#   This method uses no access token, so only basic information may be retrieved.
#   Nevertheless, this includes a wide range of data
# Returns data payload on success. Returns None on fail
def call_scryfall_03(request_url="https://api.scryfall.com/", endpoint=""):
	try:
		print("Contacting Scryfall API")
		# Waits a tenth of a second before continuing
		time.sleep(.1)

		r = requests.get(f'{request_url}{endpoint}')

		if r.status_code == 200:
			data = r.json()
			if "data" in data:
				print(f"Success! Returned {len(data['data'])} rows")
			else:
				print(f"Success! Returned data object!")

			return data
		else:
			print('Request failed, error code: ' + str(r.status_code) + ' | ' + r.reason)
			return None
	except Exception as E:
		print("Error contacting Scryfall!")
		print(E)
		return None


def get_image_from_uri(uri, file_name):
	time.sleep(.1)
	r = requests.get(url=uri, stream=True)

	if r.status_code == 200:

		with open(f"images/{file_name}", 'wb') as f:
			shutil.copyfileobj(r.raw, f)

		print('Image sucessfully Downloaded: ', file_name)
	else:
		print('Request failed, error code: ' + str(r.status_code) + ' | ' + r.reason)
		return None


def get_set_search_uri_from_set_code(set_code):
	data = call_scryfall_03(f"https://api.scryfall.com/sets/{set_code}")
	if data is not None:
		return data["search_uri"]
	else:
		return ""


def get_download_from_uri(uri, file_name):
	time.sleep(.1)
	r = requests.get(url=uri, stream=True)
	if r.status_code == 200:
		with open(file_name, 'wb') as f:
			for chunk in r.iter_content(chunk_size=8192):
				f.write(chunk)
			print('File sucessfully Downloaded: ', file_name)
	else:
		print('Request failed, error code: ' + str(r.status_code) + ' | ' + r.reason)
		return None


# Controller. Calls call_scryfall() to retrieve each creature type and returns as list of strings
def controller_get_scryfall_creature_types():
	# r = requests.get('https://api.scryfall.com/catalog/creature-types')
	r = call_scryfall_03(endpoint="catalog/creature-types")
	if r is not None:
		return r["data"]
	else:
		return {}


def controller_get_upcoming_set_svgs():
	all_sets = call_scryfall_03("https://api.scryfall.com/sets/")
	for set in all_sets["data"]:
		# print(f"{set['icon_svg_uri']}")
		set_release = datetime.fromisoformat(set["released_at"])

		if set_release > datetime.now():
			time.sleep(.1)
			r = requests.get(set["icon_svg_uri"])
			if r.status_code == 200:
				svg = r.text
				print(svg)
				filename = "csvs\\" + set["code"] + datetime.now().strftime("%Y%m%d") + ".svg"
				f = open(filename, "a")
				f.write(svg)
				f.close()


if __name__ == '__main__':
	# controller_get_upcoming_set_svgs()
	# print(get_set_search_uri_from_set_code("woe"))
	get_download_from_uri('https://data.scryfall.io/oracle-cards/oracle-cards-20240722090223.json', "downloads/oracle-cards")
