import json
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
		home_scurface = None
		percel_scurface = None
		bedrooms = None
		energy_label = None
		#raise Exception(f"Unexpected number of tags found: {len(tags)}")

	# TODO: Adjust the names to match those in the non-shallow object
	return {
		"street_name_house_number":street_name_house_number,
		"postal_code_city":postal_code_city,
		"price":price,
		"url":url,
		"home_scurface":home_scurface,
		"percel_scurface":percel_scurface,
		"bedrooms":bedrooms,
		"energy_label":energy_label
	}


def parse_individual_page(body):
	tree = html.fromstring(body)
	soup = BeautifulSoup(body, "lxml")

	## Get location data
	map_config = json.loads(tree.xpath('//*[@data-object-map-config]')[0].text.strip())
	lat, lng = map_config["lat"], map_config["lng"]

	## Get the features
	listing_features_object = soup.find(class_="object-kenmerken")

	features_dict = {}

	listing_features_dt_tags = listing_features_object.find_all("dt")
	listing_features_dd_tags = listing_features_object.find_all("dd")

	for dt_tag, dd_tag in zip(listing_features_dt_tags, listing_features_dd_tags):
		key = dt_tag.get_text(strip=True)
		first_span = dd_tag.find('span')
		value = first_span.get_text(strip=True) if first_span else None
		features_dict[key] = value

	## Realtor data
	realtor_data = soup.find_all("app-contact-broker-modal")[0].attrs

	## Price
	price_raw_object = soup.find(class_="object-header__price").text.strip()
	price_valuta, price, price_type = price_raw_object.split(" ")

	## Title
	title = soup.find(class_="object-header__title").text.strip()

	## Address data
	address_raw = soup.find(class_="object-header__subtitle").text.strip()
	postal_code_full = address_raw.split("\n")[0].strip()
	neighbourhood = address_raw.split("\n")[1].strip()

	postal_code = " ".join(postal_code_full.split()[:2])
	place = " ".join(postal_code_full.split()[2:])

	# TODO: Liked, viewed and since

	page_data = {
		"lat": lat,
		"lng": lng,
		**features_dict,
		**{f"realtorinfo__{k}": v for k, v in realtor_data.items()},
		**{k + "__nom2": v.replace("m²", "").strip()
		   for k, v in features_dict.items() if v and "m²" in v},
		"price_raw_object": price_raw_object,
		"price_valuta": price_valuta,
		"price": price,
		"price_type": price_type,
		"title": title,
		# "address_raw":address_raw,
		"postal_code_full": postal_code_full,
		"neighbourhood": neighbourhood,
		"postal_code": postal_code,
		"place": place
	}