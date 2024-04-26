import undetected_chromedriver as uc

from utils import build_search_url

profile_dir = "profile_dir"

def generate_chrome_options():
	chrome_options = uc.ChromeOptions()
	chrome_options.user_data_dir = profile_dir
	return chrome_options




npages = 20
search_url = build_search_url("koop", selected_area=["rotterdam"])


NJOBS = 5
MAX_ACTIVE_TASKS = 5

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.3"