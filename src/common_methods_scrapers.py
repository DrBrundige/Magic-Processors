from bs4 import BeautifulSoup, NavigableString
from common_methods_requests import call_web_page
import re


def scrape_sets_from_format_page(format="standard"):
	html = call_web_page(f"https://magic.wizards.com/en/formats/{format}")

	soup = BeautifulSoup(html, "html.parser")

	REGEX_LEGAL = re.compile("^What\sSets\sAre\sLegal.*$")

	sets_header = soup.find(name=True, string=REGEX_LEGAL)
	all_sets_data = sets_header.parent

	list_items = all_sets_data.findAll('li')

	format_sets = []

	for item in list_items:
		if isinstance(item.contents[0], NavigableString):
			format_sets.append(str(item.contents[0]).strip())
		else:
			# For some reason the Pioneer page isn't set up right.
			# It has additional nodes that will need to be accessed.
			this_set_code = item.find('code')
			set_string = str(this_set_code.contents[0]).strip()
			format_sets.append(set_string)

	return format_sets


if __name__ == '__main__':
	print("Scraping pages")
	print(scrape_sets_from_format_page("standard"))
	# print(scrape_sets_from_format_page("pioneer"))
	# print(scrape_sets_from_format_page("modern"))
