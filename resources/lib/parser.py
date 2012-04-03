import comm
import config
import classes
import utils
import re
import datetime
import time
from BeautifulSoup import BeautifulStoneSoup
import simplejson as json
import urllib

def parse_config(soup):
	"""	There are lots of goodies in the config we get back from the ABC.
		In particular, it gives us the URLs of all the other XML data we
		need.
	"""

	soup = soup.replace('&amp;', '&#38;')

	xml = BeautifulStoneSoup(soup)

	# should look like "rtmp://cp53909.edgefcs.net/ondemand"
	rtmp_url = xml.find('param', attrs={'name':'server_streaming'}).get('value')
	rtmp_chunks = rtmp_url.split('/')

	return {
		'rtmp_url'  : rtmp_url,
		'rtmp_host' : rtmp_chunks[2],
		'rtmp_app'  : rtmp_chunks[3],
		'api_url' : xml.find('param', attrs={'name':'api'}).get('value'),
		'categories_url' : xml.find('param', attrs={'name':'categories'}).get('value'),
	}

def parse_auth(soup, iview_config):
	"""	There are lots of goodies in the auth handshake we get back,
		but the only ones we are interested in are the RTMP URL, the auth
		token, and whether the connection is unmetered.
	"""

	xml = BeautifulStoneSoup(soup)

	# should look like "rtmp://203.18.195.10/ondemand"
	try:
		rtmp_url = xml.find('server').string

		playpath_prefix = ''

		if rtmp_url is not None:
			# Being directed to a custom streaming server (i.e. for unmetered services).
			# Currently this includes Hostworks for all unmetered ISPs except iiNet.
			rtmp_chunks = rtmp_url.split('/')
			rtmp_host = rtmp_chunks[2]
			rtmp_app = rtmp_chunks[3]
		else:
			# We are a bland generic ISP using Akamai, or we are iiNet.
			playpath_prefix = config.akamai_playpath_prefix
			rtmp_url = iview_config['rtmp_url']
			rtmp_host = iview_config['rtmp_host']
			rtmp_app = iview_config['rtmp_app']
	
		token = xml.find("token").string
		token = token.replace('&amp;', '&') # work around BeautifulSoup bug
	
	except:
		d = xbmcgui.Dialog()
		d.ok('iView Error', 'There was an iView handshake error.', 'Please try again later')
		return None

	return {
		'rtmp_url'        : rtmp_url,
		'rtmp_host'       : rtmp_host,
		'rtmp_app'        : rtmp_app,
		'playpath_prefix' : playpath_prefix,
		'token'           : token,
		'free'            : (xml.find("free").string == "yes")
	}

def create_new_series(series):
	new_series = classes.Series()
	
	#{u'a': u'9995608',
	#	u'b': u'Wildscreen Series 1',
	#	u'e': u'shopdownload',
	#	u'f': [{u'a': u'9995608',
	#			u'f': u'2010-05-30 00:00:00',
	#			u'g': u'2010-07-17 00:00:00'}]
	#}
	
	new_series.id = series['a']
	new_series.title = series['b']
	if 'c' in series:
		new_series.plot = series['c']
	if 'd' in series:
		new_series.image = series['d']
	new_series.keywords = series['e'].split(" ")
	new_series.num_episodes = int(len(series['f']))

	return new_series


def parse_index(soup):
	"""	This function parses the index, which is an overall listing
		of all programs available in iView. The index is divided into
		'series' and 'items'. Series are things like 'beached az', while
		items are things like 'beached az Episode 8'.
	"""
	series_list = []
	index = json.loads(soup)

	for series in index:
		new_series = create_new_series(series)	
		# Only include a program if isn't a 'Shop Download'
		if not new_series.has_keyword("shopdownload"):
			print "ABC iView: Found series: %s" % (new_series.get_list_title())
			if new_series.num_episodes > 0:
				series_list.append(new_series)

	return series_list


def parse_series(soup):
	""" This function parses the series list, which lists the
		the individual progams available. The items are things
		like 'beached az Episode 8' and 'beached az Episode 9'.
	"""

	# HACK: replace <abc: with < because BeautifulSoup doesn't have
	# any (obvious) way to inspect inside namespaces.
	soup = soup \
		.replace('<abc:', '<') \
		.replace('</abc:', '</') \
		.replace('<media:', '<') \
		.replace('</media:', '</') \

	# HACK: replace &amp; with &#38; because HTML entities aren't
	# valid in plain XML, but the ABC doesn't know that.
	soup = soup.replace('&amp;', '&#38;')

	series_xml = BeautifulStoneSoup(soup)

	return series_xml

def parse_series_info(soup, series):
	""" This function parses the series list, which lists the
		the individual progams available. The items are things
		like 'beached az Episode 8' and 'beached az Episode 9'.
	"""

	series_xml = parse_series(soup)

	series.thumbnail = series_xml.find('image').find('url').string
	series.description = series_xml.find('description').string

	return series
	


def parse_series_items(soup):
	""" This function parses the series list, which lists the
		the individual programs available. The items are things
		like 'beached az Episode 8' and 'beached az Episode 9'.
	"""

	series_xml = parse_series(soup)

	program_list = []
	index = series_xml.findAll('item')
	
	for program in index:
		new_program = classes.Program()
		
		try:
			new_program.title = program.find('title').string
		except:
			print "@@@ No title entry found!"
		
		try:
			new_program.episode_title = program.find('shorttitle').string
		except:
			print "@@@ No shorttitle entry found!"
		
		try:
			new_program.description = program.find('description').string
		except:
			print "@@@ No description entry found!"

		try:
			new_program.category = program.find('category').string
		except:
			print "@@@ No category entry found!"

		try:
			new_program.url = program.find('videoasset').string
		except:
			print "@@@ No url entry found!"

		try:
			new_program.rating = program.find('rating').string
		except:
			print "@@@ No rating entry found!"

		try:
			new_program.duration = program.find('content').get('duration')
		except:
			print "@@@ No duration entry found!"

		# Python 2.4 hack - time module has strptime, but datetime does not until Python 2.5
		try:
			temp_date = program.find('pubdate').string
			timestamp = time.mktime(time.strptime(temp_date, '%d/%m/%Y %H:%M:%S'))
			new_program.date = datetime.date.fromtimestamp(timestamp)
		except:
			print "@@@ No pubdate entry found!"
	
		# Check for a thumbnail
		try:
			if program.find('thumbnail').has_key('url'):
				new_program.thumbnail = program.find('thumbnail').get('url')
		except:
			print "@@@ No thumbnail entry found!"

		#print "Found program: %s" % new_program
		program_list.append(new_program)

	return program_list


def parse_category_series(category_soup, index_soup):
	category_xml = parse_series(category_soup)

	series_list = []
	categories = category_xml.findAll('item')
	index = json.loads(index_soup)

	for program in categories:
		id = -1
		try:
			if program.find('player').has_key('url'):
				id = int(program.find('player').get('url').split('/')[6])
		except:
			print "@@@ No id entry found!"

		if id != -1:
			for series in index:
				new_series = create_new_series(series)

				ok = False
				for p in series['f']:
					if int(p['a']) == id:
						ok = True
						break

				if ok == True:
					for s in series_list:
						if int(new_series.id) == int(s.id): 
							ok = False
							break

				if ok == True and not new_series.has_keyword("shopdownload"):
					print "ABC iView: Found series: %s" % (new_series.get_list_title())
					if new_series.get_image() == None or len(new_series.get_image()) == 0:
						new_series.image = program.find('thumbnail').get('url')
					if new_series.get_plot() == None or len(new_series.get_plot()) == 0:
						description = program.find('description')
						if description == None:
							new_series.plot = ''
						else:
							new_series.plot = utils.remove_cdata(description.string)
					if new_series.num_episodes > 0:
						series_list.append(new_series)

	return series_list

def parse_feed_items(soup):
	""" This function parses the feed list, which lists the
		the individual programs available. The items are things
		like 'beached az Episode 8' and 'beached az Episode 9'.
	"""

	feed_xml = parse_series(soup)

	program_list = []
	index = feed_xml.findAll('item')
	
	for program in index:
		new_program = classes.Program()
		
		try:
			new_program.title = program.find('title').string
		except:
			print "@@@ No title entry found!"
		
		try:
			new_program.episode_title = program.find('shorttitle').string
		except:
			print "@@@ No shorttitle entry found!"
		
		try:
			new_program.description = program.find('description').string
		except:
			print "@@@ No description entry found!"

		try:
			new_program.category = program.find('category').string
		except:
			print "@@@ No category entry found!"

		try:
			new_program.url = program.find('videoasset').string
		except:
			print "@@@ No url entry found!"

		try:
			new_program.rating = program.find('rating').string
		except:
			print "@@@ No rating entry found!"

		try:
			new_program.duration = program.find('content').get('duration')
		except:
			print "@@@ No duration entry found!"

		# Python 2.4 hack - time module has strptime, but datetime does not until Python 2.5
		try:
			temp_date = program.find('pubdate').string
			timestamp = time.mktime(time.strptime(temp_date, '%d/%m/%Y %H:%M:%S'))
			new_program.date = datetime.date.fromtimestamp(timestamp)
		except:
			print "@@@ No pubdate entry found!"
	
		# Check for a thumbnail
		try:
			if program.find('thumbnail').has_key('url'):
				new_program.thumbnail = program.find('thumbnail').get('url')
		except:
			print "@@@ No thumbnail entry found!"

		print "Found program: %s" % new_program
		program_list.append(new_program)

	return program_list
