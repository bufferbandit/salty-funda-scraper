from selenium.webdriver.common.by import By
from helium import Button, TextField
from urllib.parse import urlencode
from time import sleep



def reject_cookies(hla):
	if (alles_weigeren := Button("Alles weigeren")).exists():
		sleep(1)
		hla \
			.move_to_element(alles_weigeren.web_element) \
			.click() \
			.perform()


def search(hla, search_text):
	searchbox = TextField("Zoek op plaats, buurt of postcode")
	if searchbox.exists():
		searchbox_element = searchbox.web_element
		hla \
			.send_keys(search_text, searchbox_element)\
			.perform()

def get_results_items(driver):
	results_items_container = driver.find_element(By.CLASS_NAME, "pagination")
	results_items_elements = results_items_container \
		.find_elements(By.TAG_NAME, "li")
	results_items = [results_items_element.text for results_items_element in results_items_elements]
	return results_items


def get_max_items(driver):
	results_items = get_results_items(driver)
	max_item = int(results_items[-2])
	return max_item

def process_all_process_searchresults_pages(driver, base_url, max_pages, start=2):
	for x in range(start, max_pages+1):
		paginated_url = base_url + "&" + urlencode({"search_result": x})
		yield process_individual_searchresults_page(driver, paginated_url)



def process_paginated(driver, original_url):
	# Visit the search url
	driver.get(original_url)

	# Process the first page
	first_page_results = process_individual_searchresults_page(driver, original_url)
	# Get the max number of pages
	max_items = get_max_items(driver)

	# And now we know how many pages are left we can request the rest of them,
	# without rerequesting the first one which would be wasteful
	other_pages_results = list(process_all_process_searchresults_pages(driver, original_url, max_items, 2))


	return first_page_results + other_pages_results

def process_individual_searchresults_page(driver, url=None, shallow_scrape=False):

	page_results = []

	if url:driver.get(url)

	# If shallow scrape only scrape the info that is on the cards
	# card container
	search_result_items = driver.find_elements(By.XPATH, '//div[@data-test-id="search-result-item"]')
	for search_result_cards in search_result_items:
		card_data = process_search_result_item(search_result_cards)
		print(card_data)
		page_results.append(card_data)

	if not shallow_scrape:

		# Scrape an individual page

		# And add the results to the more detailed results

		...


	# Otherwise visit the urls themselves
	return page_results


def process_search_result_item(search_result_element):
	street_name_house_number = search_result_element.find_element(By.XPATH, './/h2[@data-test-id="street-name-house-number"]').text
	postal_code_city = search_result_element.find_element(By.XPATH, './/div[@data-test-id="postal-code-city"]').text
	price = search_result_element.find_element(By.XPATH, './/p[@data-test-id="price-sale"]').text
	url = search_result_element.find_element(By.XPATH, './/a[@data-test-id="object-image-link"]').get_attribute("href")

	tag_data = search_result_element.find_elements(By.TAG_NAME, "li")
	if len(tag_data) == 3:
		home_scurface = tag_data[0].text
		percel_scurface = None
		bedrooms = tag_data[1].text
		energy_label = tag_data[2].text
	elif len(tag_data) == 4:
		home_scurface = tag_data[1].text
		percel_scurface = None
		bedrooms = tag_data[2].text
		energy_label = tag_data[3].text
	elif len(tag_data) == 5:
		home_scurface = tag_data[1].text
		percel_scurface = tag_data[2].text
		bedrooms = tag_data[3].text
		energy_label = tag_data[4].text
	else:
		raise Exception(f"Unexpected number of tags found: {len(tag_data)}" )


	return [
		street_name_house_number,
		postal_code_city,
		price,
		url,
		home_scurface,
		percel_scurface,
		bedrooms,
		energy_label
	]
	#TODO: Add realtor ass well
