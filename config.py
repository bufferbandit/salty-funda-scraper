import undetected_chromedriver as uc


profile_dir = "profile_dir"


def generate_chrome_options():
	chrome_options = uc.ChromeOptions()
	chrome_options.user_data_dir = profile_dir
	return chrome_options