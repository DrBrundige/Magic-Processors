import requests
import shutil
import time


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


if __name__ == '__main__':
	print("Testing HTTP call methods")
	get_image_from_uri(
		uri="https://cards.scryfall.io/large/front/c/8/c817cf1f-c0fe-49ab-a8e9-1d09b4c15e57.jpg?1673305511",
		file_name="5c_progenitus_faeburrow_elder.jpg")
