import urllib2
import config
import parser

cache = False

def fetch_url(url):
	"""	Simple function that fetches a URL using urllib2.
		An exception is raised if an error (e.g. 404) occurs.
	"""
	http = urllib2.urlopen(urllib2.Request(url, None))
	return http.read()

def get_config():
	"""	This function fetches the iView "config". Among other things,
		it tells us an always-metered "fallback" RTMP server, and points
		us to many of iView's other XML files.
	"""
	return parser.parse_config(fetch_url(config.config_url))

def get_auth(iview_config):
	""" This function performs an authentication handshake with iView.
		Among other things, it tells us if the connection is unmetered,
		and gives us a one-time token we need to use to speak RTSP with
		ABC's servers, and tells us what the RTMP URL is.
	"""
	return parser.parse_auth(fetch_url(config.auth_url), iview_config)

def get_programme(iview_config):
	"""	This function pulls in the index, which contains the TV series
		that are available to us. The index is possibly encrypted, so we
		must decrypt it here before passing it to the parser.
	"""
	url = iview_config['api_url'] + 'seriesIndex'
	index_data = fetch_url(url)
	programme = parser.parse_index(index_data)
	return programme

def get_series_items(iview_config, series_id):
	"""	This function fetches the series detail page for the selected series,
		which contain the items (i.e. the actual episodes).
	"""
	url = config.series_url % series_id
	series_xml = fetch_url(url)
	return parser.parse_series_items(series_xml)

def get_series_info(iview_config, series):
	"""	This function fetches the series detail page for the selected series,
		which contain the items (i.e. the actual episodes).
	"""
	url = config.series_url % series.id
	series_xml = fetch_url(url)
	return parser.parse_series_info(series_xml, series)

def get_category_series(iview_config, category):
	url = 'http://tviview.abc.net.au/iview/rss/category/' + category + '.xml'
	series_xml = fetch_url(url)
	url = iview_config['api_url'] + 'seriesIndex'
	index_data = fetch_url(url)
	return parser.parse_category_series(series_xml, index_data)

def get_keyword_items(iview_config, keyword):
	"""	This function fetches the programs for the featured videos
		which contain the items (i.e. the actual episodes).
	"""
	url = iview_config['api_url'] + ('keyword=%s' % keyword)
	index_data = fetch_url(url)
	return parser.parse_index(index_data)
	
