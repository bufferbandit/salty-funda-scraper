import traceback
from multiprocessing import Lock, Manager
from multiprocessing.dummy import Pool

import requests
from selenium.webdriver.common.by import By
from helium import Button, TextField
from urllib.parse import urlencode
from time import sleep

from drivers import get_remote_driver
from utils import update_list, sel_session_request
# from driver import *
import drivers


def helium_hla_sendkeys(hla, helium_element, text):
	if helium_element.exists():
		selenium_element = helium_element.web_element
		hla_sendkeys(hla, selenium_element, text)

def hla_sendkeys(hla, selenium_element, text):
	hla \
		.reset_actions() \
		.move_to_element(selenium_element) \
		.click() \
		.send_keys(text, selenium_element) \
		.perform()


def hla_reject_cookies(hla):
	if (alles_weigeren := Button("Alles weigeren")).exists():
		# sleep(1)
		hla \
			.reset_actions() \
			.move_to_element(alles_weigeren.web_element) \
			.click() \
			.perform()

def login_if_required(driver, hla, username, password):
	if not check_if_logged_in(driver, hla):
		login(driver, hla, username, password)
	return driver.get_cookies()

def check_if_logged_in(driver, hla):
	driver.get("https://funda.nl/")
	hla_reject_cookies(hla)
	return not Button("Inloggen").exists()


def login(driver, hla, username, password):
	driver.get("https://login.funda.nl/account/login")
	hla_reject_cookies(hla)


	username_box = TextField(below="E-mailadres")
	password_box = TextField(below="Wachtwoord")

	helium_hla_sendkeys(hla, username_box, username)
	helium_hla_sendkeys(hla, password_box, password)

	log_in_button = Button("Log in")
	# hla\
	# 	.reset_actions()\
	# 	.move_to_element(log_in_button.web_element)\
	# 	.click()
	log_in_button.web_element.click()
	return driver.get_cookies()


def search(hla, search_text):
	searchbox = TextField("Zoek op plaats, buurt of postcode")
	if searchbox.exists():
		searchbox_element = searchbox.web_element
		hla \
			.reset_actions() \
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
