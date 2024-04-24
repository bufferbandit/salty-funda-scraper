import undetected_chromedriver as uc


profile_dir = "profile_dir"


chrome_options = uc.ChromeOptions()
chrome_options.user_data_dir = profile_dir