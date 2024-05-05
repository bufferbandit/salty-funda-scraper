import json
import traceback
from datetime import datetime
from xml import etree

import requests
from bs4 import BeautifulSoup
from lxml import html, etree

from utils import convert_beta_url_to_old_url, sel_session_request


def parse_max_number_of_pages(body):
	soup = BeautifulSoup(body, "lxml")
	pagination_container = soup.find(class_="pagination")
	results_items_elements = pagination_container.findAll("li")
	last_page_number = int(results_items_elements[3].text)
	print(f"[+] {last_page_number} pages found")
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
	price_raw_object = tree.xpath('.//p[@data-test-id="price-sale"]') or tree.xpath('.//p[@data-test-id="price-rent"]')
	price_raw_object = price_raw_object[0].text.strip().replace(".", "")

	if price_raw_object == "Prijs op aanvraag" or price_raw_object == "Huurprijs op aanvraag":
		price_valuta = None
		price = None
		price_type = None
	else:
		price_valuta, price, price_type, *_ = price_raw_object.split(" ")
		try:
			price = int(price.replace(".", ""))
		except ValueError as ve:
			pass

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
	# raise Exception(f"Unexpected number of tags found: {len(tags)}")

	# TODO: Adjust the names to match those in the non-shallow object
	return {
		"street_name_house_number": street_name_house_number,
		"postal_code_city": postal_code_city,
		"url": url,
		"old_url": convert_beta_url_to_old_url(url),
		"home_scurface": home_scurface,
		"percel_scurface": percel_scurface,
		"bedrooms": bedrooms,
		"energy_label": energy_label,
		"price_raw_object": price_raw_object,
		"price_valuta": price_valuta,
		"price": price,
		"price_type": price_type

	}


# TODO: We want to include the url in the object as well,
# but instead of passing it awkwardly through this parameter
# I am sure it is somewhere in the body as well and can be extracted
# also the cookies and useragent don't really belong here but done
# for reasons in a t\odo speicfied bellow
def parse_individual_page(body, url=None):
	tree = html.fromstring(body)
	soup = BeautifulSoup(body, "lxml")

	# Get the global funda id
	try:
		global_funda_id = tree.xpath('//@data-global-id')[0]
	except IndexError:
		global_funda_id = None
	try:
		published_date = tree.xpath('//@published-date')[0]
	except IndexError:
		published_date = None

	## Get location data
	try:
		map_config = json.loads(tree.xpath('//*[@data-object-map-config]')[0].text.strip())
		lat, lng = map_config["lat"], map_config["lng"]
	except IndexError:
		lat = None
		lng = None

	## Get the features
	listing_features_object = soup.find(class_="object-kenmerken") or soup.find(class_="md:mt-7")

	if not listing_features_object:
		print(f"[!] No table could be found at {url}")
		return {}

	features_dict = {}

	listing_features_dt_tags = listing_features_object.find_all("dt")
	listing_features_dd_tags = listing_features_object.find_all("dd")
	# some dd tags are just parent tags and contain nested dt and dd tags and
	# dont have a accompanying dt tag, and thus the tags get out of sync.
	# To prevent this, only include tags that have sub-tags
	parent_filtered_listing_features_dd_tags = [dd_tag for dd_tag in listing_features_dd_tags if not (dd_tag.find_all("dt") + dd_tag.find_all("dd"))]

	if len(parent_filtered_listing_features_dd_tags) != len(listing_features_dt_tags):
		raise Exception(f"The number of dt's does not match the number of filtered dd's! " +
						f"len(dt's)={len(listing_features_dt_tags)}, " +
						f"len(filtered_dd's)={len(parent_filtered_listing_features_dd_tags)}")

	for dt_tag, dd_tag in zip(listing_features_dt_tags, parent_filtered_listing_features_dd_tags):
		key = dt_tag.get_text(strip=True)
		first_span = dd_tag.get_text(strip=True)
		# value = first_span.get_text(strip=True) if first_span else None
		value = first_span
		features_dict[key] = value

	# If contains VvE info, fix the formatting

	vve_valuta = None
	vve_period_fullstr = None
	vve_period_only = None
	vve_price_flt = None

	try:
		if vve_object_raw := features_dict.get("Bijdrage VvE"):
			vve_valuta, vve_price, *vve_period = vve_object_raw.split()
			vve_period_fullstr = " ".join(vve_period)
			vve_period_only = vve_period[-1]
			vve_price_flt = float(vve_price.replace(",", "."))
	except:
		pass

	## Realtor data
	try:
		# TODO: Also get the realtor id
		#			 ...
		#            'makelaarVestigingnummer' : '62887',
		#            'makelaarsvereniging' : 'Vbo',
		realtor_data = soup.find_all("app-contact-broker-modal")[0].attrs
	except:
		realtor_data = {}

	## Price
	price_raw_object = (
			soup.find(class_="object-header__price") or
			soup.find(class_="flex gap-2 font-bold") or
			soup.find(class_="flex flex-col text-xl") or
			soup.find(class_="flex flex-col pt-3 text-xl font-bold")

	).text.strip()

	if price_raw_object == "Prijs op aanvraag" or price_raw_object == "Huurprijs op aanvraag":
		price_valuta = None
		price = None
		price_type = None
	else:
		price_valuta, price, price_type, *_ = price_raw_object.split(" ")
		try:
			price = int(price.replace(".", ""))
		except ValueError as ve:
			pass

	## Title
	title = (
			soup.find(class_="object-header__title") or
			soup.find(class_="block text-2xl font-bold md:text-3xl lg:text-4xl")
	).text.strip()

	## Address data
	address_raw = (
			soup.find(class_="object-header__subtitle") or
			soup.find(class_="block text-2xl font-bold md:text-3xl lg:text-4xl")
	).text.strip()
	postal_code_full = address_raw.split("\n")[0].strip()
	try:
		neighbourhood = address_raw.split("\n")[1].strip()
	except:
		neighbourhood = None

	postal_code = " ".join(postal_code_full.split()[:2])
	place = " ".join(postal_code_full.split()[2:])

	# TODO: Neighbourgoodinfo
	# https://marketinsights.funda.io/v2/LocalInsights/preview/{city}/{neighbourhood_name}

	# TODO: Maybe think a bit better about where to do the fetching.
	#  This kinda is a parsing-only thing here and it's not architectually sound
	try:
		if global_funda_id:
			object_statistics_url = "https://marketinsights.funda.io/v1/objectinsights/" + global_funda_id
			# res = sel_session_request("get", object_statistics_url, _selenium_cookies, _selenium_useragent)
			res = requests.get(object_statistics_url)
			if res.status_code == 204:
				object_statistics = {}
			else:
				object_statistics = res.json()
		else:
			object_statistics = {}
	except Exception as e:
		# traceback.print_exception(e)
		object_statistics = {}

	page_data = {
		"global_funda_id": global_funda_id,
		"lat": lat,
		"lng": lng,
		**features_dict,
		**{f"realtorinfo__{k}": v for k, v in realtor_data.items()},
		**{f"objectstatistics__{k}": v for k, v in object_statistics.items()},
		**{k + "__nom2": v.replace("m²", "").strip()
		   for k, v in features_dict.items() if v and "m²" in v},
		"price_raw_object": price_raw_object,
		"price_valuta": price_valuta,
		"price": price,
		"prijs": price,  # bilingual shit
		"price_type": price_type,
		"title": title,
		# "address_raw":address_raw,
		"postal_code_full": postal_code_full,
		"neighbourhood": neighbourhood,
		"postal_code": postal_code,
		"place": place,
		"url": url,
		"old_url": convert_beta_url_to_old_url(url),
		"published_date": published_date,
		"requested_at": datetime.now().strftime("%d-%m-%Y-%H-%M-%S"),
		"vve_period_fullstr": vve_period_fullstr,
		"vve_valuta": vve_valuta,
		"vve_period_only": vve_period_only,
		"vve_price_flt": vve_price_flt,
	}
	return page_data
