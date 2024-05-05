import inspect
import traceback
from urllib.parse import urlencode

import requests
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver


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


	return requests.request(method=method,url=url,headers=headers,cookies=requests_cookies, *args, **kwargs)



# Formatting functions
range_to_str = lambda r: f"\"{r[0]}-{r[1]}\""
list_to_list_repr = lambda l: str(l).replace('\'', "\"")


# koop|huur
def build_search_url(
		form_of_living: str,
		selected_area: list[str] = None,
		object_type: list[str] = None,
		price_range: tuple[int, int] = None,
		publication_date: int = None,
		availability: list[str] = None,
		floor_area_range: tuple[int, int] = None,
		plot_area_range: tuple[int, int] = None,
		rooms_range: tuple[int, int] = None,
		bedrooms_range: tuple[int, int] = None,
		energy_label: list[str] = None,
		exterior_space_type: list[str] = None,
		exterior_space_garden_orientation: list[str] = None,
		exterior_space_garden_size_range: tuple[int, int] = None,
		construction_type: list[str] = None,
		zoning: list[str] = None,
		free_text_search: list[str] = None,
		construction_period: list[str] = None,
		garage_capacity_range: tuple[int, int] = None,
		amenities: list[str] = None,
		type: list[str] = None,
		open_house: list[str] = None,
):
	base_url = f"https://www.funda.nl/zoeken/{form_of_living}?"

	params = {}

	if selected_area:
		params["selected_area"] = list_to_list_repr(selected_area)
	if object_type:
		params["object_type"] = list_to_list_repr(object_type)
	if price_range:
		params["price"] = range_to_str(price_range)
	if publication_date:
		params["publication_date"] = range_to_str(publication_date)
	if availability:
		params["availability"] = list_to_list_repr(availability)
	if floor_area_range:
		params["floor_area"] = range_to_str(floor_area_range)
	if plot_area_range:
		params["plot_area"] = range_to_str(plot_area_range)
	if rooms_range:
		params["rooms"] = range_to_str(rooms_range)
	if bedrooms_range:
		params["bedrooms"] = range_to_str(bedrooms_range)
	if energy_label:
		params["energy_label"] = list_to_list_repr(energy_label)
	if exterior_space_type:
		params["exterior_space_type"] = list_to_list_repr(exterior_space_type)
	if exterior_space_garden_orientation:
		params["exterior_space_garden_orientation"] = list_to_list_repr(exterior_space_garden_orientation)
	if exterior_space_garden_size_range:
		params["exterior_space_garden_size"] = range_to_str(exterior_space_garden_size_range)
	if construction_type:
		params["construction_type"] = list_to_list_repr(construction_type)
	if zoning:
		params["zoning"] = list_to_list_repr(zoning)
	if free_text_search:
		params["free_text_search"] = list_to_list_repr(free_text_search)
	if construction_period:
		params["construction_period"] = list_to_list_repr(construction_period)
	if garage_capacity_range:
		params["garage_capacity"] = range_to_str(garage_capacity_range)
	if amenities:
		params["amenities"] = list_to_list_repr(amenities)
	if type:
		params["type"] = list_to_list_repr(type),
	if open_house:
		params["open_house"] = list_to_list_repr(open_house)

	# "https://www.funda.nl/zoeken/koop?selected_area=["amsterdam"]&object_type=["house"]&price="75000-450000"&publication_date="1"&availability=["available","negotiations","unavailable"]&floor_area="50-250"&plot_area="250-5000"&rooms="1-5"&bedrooms="1-5"&energy_label=["A+++++","D","A++++"]&exterior_space_type=["balcony","terrace"]&exterior_space_garden_orientation=["east","north"]&exterior_space_garden_size="25-500"&construction_type=["newly_built","resale"]&zoning=["recreational","residential"]&free_text_search=["warmtepomp","dakteras"]&construction_period=["before_1906","from_1906_to_1930"]&garage_capacity="1-5"&amenities=["bathtub","central_heating_boiler"]&type=["single","group"]&open_house=["all","today","coming_weekend"]"

	return base_url + urlencode(params)



def flatten_ndlist(arg):
	if not isinstance(arg, list): # if not list
		return [arg]
	return [x for sub in arg for x in flatten_ndlist(sub)]


def convert_beta_url_to_old_url(url):
	try:
		url = url.replace("/detail", "")
		id = url.split("/")[-2]
		place_name = url.split("/")[-4]
		url = url.replace(place_name,place_name.replace("-","<DASH>"))
		url = url.replace(id + "/", "")
		dashed_parts = url.split("-")
		dashed_parts.insert(1, id)
		new_url = "-".join(dashed_parts)
		new_url = new_url.replace("<DASH>","-")
		return new_url
	except Exception as e:
		# traceback.print_exception(e)
		return None



def standardize_dicts(list_of_dicts):
	# Step 1: Find all unique keys
	all_keys = set().union(*(d.keys() for d in list_of_dicts))
	# Step 2: Update dictionaries with missing keys
	for d in list_of_dicts:
		for key in all_keys:
			d.setdefault(key, None)
	return list_of_dicts