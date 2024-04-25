from xml import etree

from bs4 import BeautifulSoup
from lxml import html, etree


def parse_max_number_of_pages(body):
	soup = BeautifulSoup(body, "lxml")
	pagination_container = soup.find(class_="pagination")
	results_items_elements = pagination_container.findAll("li")
	last_page_number = int(results_items_elements[3].text)
	# pages_container = driver.find_element(By.CLASS_NAME, "pagination")
	# results_items_elements = pages_container \
	# 	.find_elements(By.TAG_NAME, "li")
	# results_items = [results_items_element.text for results_items_element in results_items_elements]
	return last_page_number


def parse_searchresults_page(body):
	tree = html.fromstring(body)
	search_result_items = tree.xpath('//div[@data-test-id="search-result-item"]')
	for search_result_card in search_result_items:
		card_html = etree.tostring(search_result_card).decode("utf-8")
		yield parse_individual_searchresult_card(card_html)


def parse_individual_searchresult_card(body):
	tree = html.fromstring(body)
	soup = BeautifulSoup(body, "lxml")


	street_name_house_number = tree.xpath('.//h2[@data-test-id="street-name-house-number"]')[0].text.strip()
	postal_code_city = tree.xpath('.//div[@data-test-id="postal-code-city"]')[0].text.strip()
	price = tree.xpath('.//p[@data-test-id="price-sale"]')[0].text.strip()
	url = tree.xpath('.//a[@data-test-id="object-image-link"]')[0].attrib["href"].strip()

	tags = soup.findAll("li")
	if len(tags) == 3:
		home_scurface = tags[0].text.strip()
		percel_scurface = None
		bedrooms = tags[1].text.strip()
		energy_label = tags[2].text.strip()
	elif len(tags) == 4:
		home_scurface = tags[1].text.strip()
		percel_scurface = None
		bedrooms = tags[2].text.strip()
		energy_label = tags[3].text.strip()
	elif len(tags) == 5:
		home_scurface = tags[1].text.strip()
		percel_scurface = tags[2].text.strip()
		bedrooms = tags[3].text.strip()
		energy_label = tags[4].text.strip()
	elif len(tags) == 6:
		# 0 is "blikvanger"
		# 1 is "nieuw"
		# 2 is "open huis"
		home_scurface = tags[3].text.strip()
		bedrooms = tags[4].text.strip()
		energy_label = tags[5].text.strip()
		percel_scurface = None
	else:
		raise Exception(f"Unexpected number of tags found: {len(tags)}")


	return {
		"street_name_house_number":street_name_house_number,
		"postal_code_city":postal_code_city,
		"price":price,
		"url":url,
		"home_scurface":home_scurface,
		"percel_scurface":percel_scurface,
		"bedrooms":bedrooms,
		"energy_label":energy_label

		# TODO: Add realtor ass well
	}