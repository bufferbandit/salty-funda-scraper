from urllib.parse import urlencode

from funda_parse import parse_searchresults_page, parse_max_number_of_pages
from utils import sel_session_request
import drivers


def req_and_parse_searchpage(search_url, max_page=None, in_recursion=False):

	selenium_cookies = drivers.selenium_cookies
	selenium_useragent = drivers.selenium_useragent

	res = sel_session_request("get", search_url, selenium_cookies, selenium_useragent)
	body = res.text

	searchresults_for_page = list(parse_searchresults_page(body))
	yield searchresults_for_page

	if not in_recursion:
		# Get the highest page number
		max_page = max_page or parse_max_number_of_pages(body)
		for x in range(2, max_page+1):
			paginated_url = search_url + "&" + urlencode({"search_result": x})
			yield from req_and_parse_searchpage(paginated_url, in_recursion=True)

	# If no page is given, we can assume we are making the first request
	# and the number of pages is not known yet

	# 	# If max page is None return
	# 	if max_page is None:
	# 		return
	# 	# Otherwise go on and get the max page from the body
	# 	max_page = parse_max_number_of_pages(body)
	# 	# Loop through all of them
	# 	for x in range(max_page):
	# 		# Create a new url
	# 		paginated_url = search_url + "&" + search_url({"search_result": x})
	# 		yield list(req_and_parse_searchpage(paginated_url))
	# # If a page is given, don't get the




	# searchresult_page_data = list(parse_searchresults_page(body))
	# yield searchresult_page_data


	# max_number_of_pages = pages or get_max_number_of_pages(body)
	# for x in range(max_number_of_pages):
	# 	paginated_url = search_url + "&" + search_url({"search_result": x})
	#
	# 	#yield list(parse_searchresults_page(paginated_url))