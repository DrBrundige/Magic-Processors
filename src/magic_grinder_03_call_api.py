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
	controller_get_upcoming_set_svgs()
