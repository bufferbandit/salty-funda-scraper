from pprint import pprint

from helium import start_chrome, start_firefox, set_driver, click
from HLISA.hlisa_action_chains import HLISA_ActionChains

from funda_requests import req_and_parse_searchpage
from selenium_functions import *
from drivers import create_driver
import usersecrets
import drivers
from utils import build_search_url, flatten_ndlist


# auto add selenium






def main_flow(selenium_driver, hla):

	drivers.selenium_cookies = login_if_required(selenium_driver, hla, usersecrets.USERNAME, usersecrets.PASSWORD)
	drivers.selenium_useragent = selenium_driver.execute_script("return navigator.userAgent")
	selenium_driver.quit()

	# Go to the search page
	area = ["rotterdam"]
	search_url = build_search_url("koop", area)

	all_searchpages_results = []
	serachpages_results = req_and_parse_searchpage(search_url,3)
	for searchpage_result in serachpages_results:
		searchpage_results = list(searchpage_result)
		all_searchpages_results.append(searchpage_results)

	# For some super strange reason no matter what I try the
	# list of the paginated searchresults keeps being n-dimensional.
	# My intention was to create a generator that gives individual search
	# results, but when trying to use yield from on a list of dicts
	# seems to be giving the keys only, so next best plan is this
	# dumb yet simple solution and just flatten the array after the fact.
	# Appart from the fact that this is not really a good solution because
	# it does not address the rootcause, it might also become problematic
	# in practice when the list becomes really big.
	pprint(flatten_ndlist(all_searchpages_results))

	pass
	input("Press any key to exit...")


if __name__ == "__main__":

	drivers.driver = create_driver()
	drivers.hla = HLISA_ActionChains(drivers.driver, browser_resets_cursor_location=False)
	set_driver(drivers.driver)

	# Browsing
	main_flow(drivers.driver, drivers.hla)
	pass
