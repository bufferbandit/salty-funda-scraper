import undetected_chromedriver as uc

from utils import build_search_url

profile_dir = "profile_dir"

def generate_chrome_options():
	chrome_options = uc.ChromeOptions()
	chrome_options.user_data_dir = profile_dir
	return chrome_options




npages = 1
search_url = build_search_url("koop", selected_area=["rotterdam"])


NJOBS = 5
MAX_ACTIVE_TASKS = 5
