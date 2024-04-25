import traceback
from multiprocessing import Pool
from pprint import pprint
from urllib.parse import urlencode

from mpire import WorkerPool

from funda_parse import parse_searchresults_page, parse_max_number_of_pages
from utils import sel_session_request
import drivers


# def threaded_req_and_parse_searchpage(*args):
# 	print(args)
# 	# return list(req_and_parse_searchpage(url, in_recursion=True, _selenium_cookies=_selenium_cookies, _selenium_useragent=_selenium_useragent))



def req_and_parse_searchpage(search_url, max_page=None, in_recursion=False, _selenium_cookies=None, _selenium_useragent=None):

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

		pool = WorkerPool(5, use_dill=True)
		results = pool.map(
			func=lambda url, selenium_cookies, selenium_useragent: list(
				req_and_parse_searchpage(
					url,
					in_recursion=True,
					_selenium_cookies=selenium_cookies,
					_selenium_useragent=selenium_useragent,
				)
			),
			iterable_of_args=[(url, selenium_cookies, selenium_useragent) for url in urls],
			progress_bar=True,
			progress_bar_style="rich",
		)
		yield results




