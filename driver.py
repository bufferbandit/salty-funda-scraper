import multiprocessing
from functools import partial

import undetected_chromedriver as uc
from HLISA.hlisa_action_chains import HLISA_ActionChains
from selenium import webdriver
import config


def create_driver():
	try:
		driver = uc.Chrome(headless=False, options=config.generate_chrome_options())  # version_main= )
	finally:
		driver.quit()
	return driver


def get_remote_driver(executor_url, session_id):
	driver = webdriver.Remote(
		command_executor=executor_url,
		options=config.chrome_options
	)
	driver.session_id = session_id
	return driver


