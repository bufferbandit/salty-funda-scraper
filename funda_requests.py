

from funda_parse import parse_searchresults_page, parse_max_number_of_pages, parse_individual_page
from utils import sel_session_request, flatten_ndlist, standardize_dicts
from urllib.parse import urlencode
from mpire import WorkerPool
import drivers
import config


pool = WorkerPool(config.NJOBS, enable_insights=True, use_dill=True)


def req_and_parse_pages(page_urls):
	global pool
	# pool = WorkerPool(5, use_dill=True)
	results = pool.map(
		func=lambda url, selenium_cookies, selenium_useragent:
			req_and_parse_individual_page(
				url,
				_selenium_cookies=selenium_cookies,
				_selenium_useragent=selenium_useragent,
		),
		iterable_of_args=[(url, drivers.selenium_cookies, drivers.selenium_useragent) for url in page_urls],
		progress_bar=True,
		progress_bar_style="rich",
		max_tasks_active=config.MAX_ACTIVE_TASKS
	)

	# Note see comments in req_and_parse_searchpage
	flattened_list = flatten_ndlist(results)
	# Note see comments in req_and_parse_searchpage
	standardized_dict = standardize_dicts(flattened_list)
	return standardized_dict

def req_and_parse_individual_page(page_url, _selenium_cookies=None, _selenium_useragent=None):
	res = sel_session_request("get", page_url, _selenium_cookies, _selenium_useragent)
	return parse_individual_page(res.text, page_url)


def req_and_parse_searchpage(search_url, max_page=None):
	all_searchpages_results = []
	serachpages_results = _req_and_parse_searchpage(search_url, max_page)
	for searchpage_result in serachpages_results:
		searchpage_results = list(searchpage_result)
		all_searchpages_results.append(searchpage_results)

	# For some super strange reason no matter what I try the
	# list of the paginated searchresults keeps being n-dimensional.
	# My intention was to create a generator that gives individual search
	# results, but when trying to use yield from on a list of dicts
	# seems to be giving the keys only, so next best plan is this
	# dumb yet simple solution and just flatten the array after the fact.
	# Appart from the fact that this is not really a good solution because
	# it does not address the rootcause, it might also become problematic
	# in practice when the list becomes really big.
	flattened_list = flatten_ndlist(all_searchpages_results)

	# Yet another trick has to be done here. Apparently some dicts have keys that
	# otehrs do not. To fix this, get all keys from all objects and when another
	# object does not have those add them and add None to them
	standardized_dict = standardize_dicts(flattened_list)

	return standardized_dict




def _req_and_parse_searchpage(search_url, max_page=None, in_recursion=False, _selenium_cookies=None, _selenium_useragent=None):

	# Default options are added for when in threaded mode, the thread cannot get variables from the module
	selenium_cookies = _selenium_cookies or drivers.selenium_cookies
	selenium_useragent = _selenium_useragent or drivers.selenium_useragent

	res = sel_session_request("get", search_url, selenium_cookies, selenium_useragent)
	body = res.text

	searchresults_for_page = list(parse_searchresults_page(body))
	yield searchresults_for_page



	if not in_recursion:
		# Get the highest page number
		max_page = max_page or parse_max_number_of_pages(body)
		urls = [search_url + "&" + urlencode({"search_result": x}) for x in range(max_page)]

		global pool
		# pool = WorkerPool(5, use_dill=True)
		results = pool.map(
			func=lambda url, selenium_cookies, selenium_useragent: list(
				_req_and_parse_searchpage(
					url,
					in_recursion=True,
					_selenium_cookies=selenium_cookies,
					_selenium_useragent=selenium_useragent,
				)
			),
			iterable_of_args=[(url, selenium_cookies, selenium_useragent) for url in urls],
			progress_bar=True,
			progress_bar_style="rich",
			max_tasks_active=config.MAX_ACTIVE_TASKS
		)
		yield results




