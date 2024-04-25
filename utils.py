import inspect

import requests
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver

import config


# executor_url = driver.command_executor._url
# session_id = driver.session_id


def update_list(list, index, value):
	list[index] = value


def sel_session_request(method, url, selenium_cookies, selenium_useragent=None, *args, **kwargs):

	requests_cookies = {}

	for c in selenium_cookies:
		requests_cookies[c["name"]] = c["value"]

	# Check if headers are already given as argument
	headers = kwargs.get("headers") or {}
	# Then add it to the new headers
	headers["User-Agent"] = selenium_useragent
	# Remove the headers from the arguments
	kwargs.pop("headers", None)

	# headers = {"":driver_useragent}

	# return requests.get(*args, **kwargs, cookies=requests_cookies)
	return requests.request(method=method,url=url,headers=headers, *args, **kwargs)
