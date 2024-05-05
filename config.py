import undetected_chromedriver as uc

from utils import build_search_url

profile_dir = "profile_dir"

def generate_chrome_options():
	chrome_options = uc.ChromeOptions()
	chrome_options.user_data_dir = profile_dir
	return chrome_options




npages = None
search_url = build_search_url("koop", selected_area=["rotterdam"], availability=["available"])


NJOBS = 20
MAX_ACTIVE_TASKS = 8

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.3"