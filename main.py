import csv
from pprint import pprint

from helium import start_chrome, start_firefox, set_driver, click
from HLISA.hlisa_action_chains import HLISA_ActionChains

from funda_requests import req_and_parse_searchpage, req_and_parse_pages
from selenium_functions import *
from drivers import create_driver
import usersecrets
import drivers
from utils import build_search_url, flatten_ndlist
from datetime import datetime


# auto add selenium






def main_flow(selenium_driver, hla):

	drivers.selenium_cookies = login_if_required(selenium_driver, hla, usersecrets.USERNAME, usersecrets.PASSWORD)
	drivers.selenium_useragent = selenium_driver.execute_script("return navigator.userAgent")
	selenium_driver.quit()

	# Go to the search page
	area = ["rotterdam"]
	search_url = build_search_url("koop", area)

	search_results = req_and_parse_searchpage(search_url)
	# pprint(search_results)

	pages_data = req_and_parse_pages([sr["url"] for sr in search_results])

	pprint(pages_data)



	with open("funda_data-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".csv", mode="w", newline="") as file:
		fieldnames = pages_data[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(pages_data)



if __name__ == "__main__":

	drivers.driver = create_driver()
	drivers.hla = HLISA_ActionChains(drivers.driver, browser_resets_cursor_location=False)
	set_driver(drivers.driver)

	# Browsing
	main_flow(drivers.driver, drivers.hla)
	pass
