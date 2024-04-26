import undetected_chromedriver as uc
from selenium import webdriver
import config


def create_driver():
	chrome_options = config.generate_chrome_options()
	driver = uc.Chrome(headless=False, options=chrome_options)  # version_main= )
	return driver


def get_remote_driver(executor_url, session_id):
	try:
		chrome_options = config.generate_chrome_options()
		driver = webdriver.Remote(
			command_executor=executor_url,
			options=chrome_options
		)
		driver.session_id = session_id
	finally:
		driver.quit()
		return driver



hla = None

driver = None
selenium_cookies = []
selenium_useragent = ""

