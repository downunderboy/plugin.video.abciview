import re
import utils
import datetime
import urllib
import time

class Series(object):

	def __init__(self):
		self.plot = ''
		self.image = ''
		pass

	def __repr__(self):
		return self.title

	def __cmp__(self, other):
		return cmp(self.title, other.title)

	def get_title(self):
		""" Return the program title, including the Series X part
			on the end.
		"""
		return utils.descape(self.title)

	def get_plot(self):
		""" Return the series plot.
		"""
		return utils.descape(self.plot)

	def get_image(self):
		""" Return the series image.
		"""
		return utils.descape(self.image)

	def get_list_title(self):
		""" Return the program title with the number of episodes
			together for the XBMC list
		"""
		return "%s (%d)" % (self.get_title(), self.get_num_episodes())

	def get_season(self):
		""" Return an integer of the Series, discovered by a regular
			expression from the orginal title, unless its not available,
			then a 0 will be returned.
		"""
		season = re.search('^.* Series (?P<season>\d+)$', self.get_title())
		if title is None:
			return 0
		return int(series.group('season'))

	def get_num_episodes(self):
		return self.num_episodes

	def get_keywords(self):
		""" Return a list of keywords
		"""
		if self.keywords != None:
			return (", ").join(self.keywords).title().replace('Abc1', 'ABC1').replace('Abc2', 'ABC2').replace('Abc3', 'ABC3').replace('Abc4', 'ABC4')
		else:
			return ''

	def get_runtime(self):
		return self.runtime
	
	def has_keyword(self, keyword):
		""" Returns true if a keyword is found
		"""
		for kw in self.keywords:
			if kw == keyword:
				return True
		return False


class Program(object):

	def __init__(self):
		self.id = -1
		self.series_id = -1
		self.title = ''
		self.episode_title = ""
		self.description = ''
		self.duration = ''
		self.category = 'Unknown'
		self.keywords = []
		self.rating = 'PG'
		self.duration = '00:00'
		self.date = datetime.datetime.now()
		self.thumbnail = ''
		self.url = ''

	def __repr__(self):
		return self.title

	def __cmp__(self, other):
		return cmp(self.title, other.title)

	def get_title(self):
		""" Return the program title, including the Series X part
			on the end.
		"""
		return utils.descape(self.title)

	def get_show_title(self):
		""" Return the show title with the 'Series X Episode X' or 'XX/XX/XX' part stripped
			off.
		"""
		title = re.search('^(?P<title>.*) (?:Series \d+ Episode \d+|\d\d/\d\d/\d\d)', self.get_title())
		if title is None:
			return self.get_title()
		return utils.descape(title.group('title'))

	def get_episode_title(self):
		""" Return a string of the shorttitle entry, unless its	not 
			available, then we'll just use the program title instead.
		"""
		if self.episode_title and self.episode_title != ' ':
			return utils.descape(self.episode_title)

		return self.get_show_title()

	def get_list_title(self):
		""" Return a string of the title, nicely formatted for XBMC list
		"""
		title = self.get_show_title()
		ep_title = self.get_episode_title()

		if (ep_title != title and len(ep_title)>2):
			title = "%s: %s" % (title, ep_title)
		elif (self.get_season() and self.get_episode()):
			title = "%s (%dx%d)" % (title, self.get_season(), self.get_episode())
		else:
			title = self.get_title()

		return title

	def get_description(self):
		""" Return a string the program description, after running it through
			the descape.
		"""
		return utils.descape(self.description)

	def get_category(self):
		""" Return a string of the category. E.g. Comedy
		"""
		return utils.descape(self.category)

	def get_rating(self):
		""" Return a string of the rating. E.g. PG, MA
		"""
		return utils.descape(self.rating)

	def get_duration(self):
		""" Return a string representing the duration of the program.
			E.g. 00:30 (30 minutes)
		"""
		return self.duration

	def get_date(self):
		""" Return a string of the date in the format 2010-02-28
			which is useful for XBMC labels.
		"""
		return self.date.strftime("%Y-%m-%d")

	def get_year(self):
		""" Return an integer of the year of publish date
		"""
		return self.date.year

	def get_season(self):
		""" Return an integer of the Series, discovered by a regular
			expression from the orginal title, unless its not available,
			then a 0 will be returned.
		"""
		season = re.search('Series (?P<season>\d+)', self.get_title())
		if season is None:
			return self.get_year()
		return int(season.group('season'))

	def get_episode(self):
		""" Return an integer of the Episode, discovered by a regular
			expression from the orginal title, unless its not available,
			then a 0 will be returned.
		"""
		episode = re.search('Episode (?P<episode>\d+)', self.get_title())
		if episode is None:
			return 0
		return int(episode.group('episode'))

	def get_thumbnail(self):
		return self.thumbnail

	def get_xbmc_list_item(self):
		""" Returns a dict of program information, in the format which
			XBMC requires for video metadata.
		"""

		info_dict = {	'tvshowtitle': self.get_show_title(),
						'title': self.get_episode_title(),
						'genre': self.get_category(),
						'plot': self.get_description(),
						'plotoutline': self.get_description(),
						'duration': self.get_duration(),
						'year': self.get_year(),
						'aired': self.get_date(),
						'season': self.get_season(),
						'episode': self.get_episode(),
						'mpaa': self.get_rating(),
					}

		return info_dict

	def make_xbmc_url(self):
		""" Returns a string which represents the program object, but in
			a format suitable for passing as a URL.
		"""
		url = "%s=%s" % ("id", self.id)
		url = "%s&%s=%s" % (url, "title", urllib.quote_plus(self.title)) 
		url = "%s&%s=%s" % (url, "episode_title", urllib.quote_plus(self.episode_title)) 
		url = "%s&%s=%s" % (url, "description", urllib.quote_plus(self.description.encode('ascii','replace'))) 
		url = "%s&%s=%s" % (url, "duration", urllib.quote_plus(self.duration)) 
		url = "%s&%s=%s" % (url, "category", urllib.quote_plus(self.category))
		url = "%s&%s=%s" % (url, "url", urllib.quote_plus(self.url))
		url = "%s&%s=%s" % (url, "rating", self.rating) 
		url = "%s&%s=%s" % (url, "duration", urllib.quote_plus(self.duration)) 
		url = "%s&%s=%s" % (url, "date", self.date.strftime("%d/%m/%Y %H:%M:%S"))
		url = "%s&%s=%s" % (url, "thumbnail", urllib.quote_plus(self.thumbnail)) 
		return url

	def parse_xbmc_url(self, string):
		""" Takes a string input which is a URL representation of the 
			program object
		"""
		d = utils.get_url(string)
		self.title = d['title']
		self.episode_title = utils.remove_cdata(d['episode_title'])
		self.description = d['description']
		self.duration = d['duration']
		self.category = d['category']
		self.url = d['url']
		self.rating = d['rating']
		timestamp = time.mktime(time.strptime(d['date'], '%d/%m/%Y %H:%M:%S'))
		self.date = datetime.date.fromtimestamp(timestamp)
		self.thumbnail = d['thumbnail']

