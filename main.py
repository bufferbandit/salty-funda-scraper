
from utils import build_search_url, flatten_ndlist, convert_beta_url_to_old_url
from funda_requests import req_and_parse_searchpage, req_and_parse_pages
from helium import start_chrome, start_firefox, set_driver, click
from HLISA.hlisa_action_chains import HLISA_ActionChains
from mpire.dashboard import start_dashboard
from drivers import create_driver
from selenium_functions import *
from datetime import datetime
from pprint import pprint
import usersecrets
import webbrowser
import drivers
import config
import csv
import os





# auto add selenium



# def set_cookies_and_useragent(cookies, useragent):
# 	drivers.selenium_useragent = useragent
# 	drivers.selenium_cookies =  cookies

def main_flow(selenium_driver=None, hla=None):

	# TODO: Find a way to put this better then it is now. The driver thing does
	# not really quite belong here
	if selenium_driver and hla:
		drivers.selenium_cookies = login_if_required(selenium_driver, hla, usersecrets.USERNAME, usersecrets.PASSWORD)
		drivers.selenium_useragent = selenium_driver.execute_script("return navigator.userAgent")
		selenium_driver.quit()
	else:
		drivers.selenium_useragent = config.user_agent
		drivers.selenium_cookies = []

	# Go to the search page
	search_results = req_and_parse_searchpage(config.search_url, config.npages)
	pages_data = req_and_parse_pages([convert_beta_url_to_old_url(sr["url"]) for sr in search_results])

	os.makedirs("out", exist_ok=True)
	with open("out/funda_data-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".csv", mode="w", newline="") as file:
		fieldnames = pages_data[0].keys()
		writer = csv.DictWriter(file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(pages_data)



if __name__ == "__main__":
	dashboard_details = start_dashboard(range(9000, 9100))
	pprint(dashboard_details)

	url_str = f"http://{dashboard_details['manager_host']}:{dashboard_details['dashboard_port_nr']}"
	print(f"[+] Opening url: {url_str}")
	webbrowser.open(url_str)

	drivers.driver = create_driver()
	drivers.hla = HLISA_ActionChains(drivers.driver, browser_resets_cursor_location=False)
	set_driver(drivers.driver)


	# Browsing
	main_flow(drivers.driver, drivers.hla)
	pass
