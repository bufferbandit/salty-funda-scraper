import inspect

import requests
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver

import config


# executor_url = driver.command_executor._url
# session_id = driver.session_id


def update_list(list, index, value):
	list[index] = value


def get_with_selenium_cookies(*args, **kwargs):
	requests_cookies = {}

	for c in kwargs["selenium_cookies"]:
		requests_cookies[c["name"]] = c["value"]

	if "selenium_cookies" in kwargs:
		del kwargs["selenium_cookies"]

	return requests.get(*args, **kwargs, cookies=requests_cookies)
