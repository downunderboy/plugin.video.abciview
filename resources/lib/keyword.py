"""
	Keyword module: fetches a list of categories to use as folders
"""

# main imports
import sys, os, re, urllib2, urllib
import comm
import xbmcsettings as settings

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

__addonid__ = 'plugin.video.abciview'
__settings__ = settings.Settings(__addonid__, sys.argv)
__fanart__ = __settings__.get_path('fanart.png')

def get_keyword(keyword):
	iview_config = comm.get_config()
	keyword = comm.get_keyword_items(iview_config, keyword)
	return keyword

def make_list(keyword):
	series = get_keyword(keyword)
	series.sort()

	# fill media list
	ok = fill_media_list(series)
	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def fill_media_list(series_list):
	iview_config = comm.get_config()
	ok = True
	# enumerate through the list of categories and add the item to the media list
	for s in series_list:
		url = "%s?series_id=%s" % (sys.argv[0], s.id)
		if s.get_image() and len(s.get_image()) > 0:
			icon = s.get_image()
		else:
			icon = __settings__.get_path('resources/images/abc.png')
		listitem = xbmcgui.ListItem(s.get_title(), iconImage=icon, thumbnailImage=icon)
		listitem.setProperty('fanart_image', icon)
		listitem.setInfo('video', {'episode':s.get_num_episodes(), 'plot': s.get_plot(), 'genre': s.get_keywords()})
		# add the item to the media list
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True, totalItems=len(series_list))
		# if user cancels, call raise to exit loop
	if (not ok): 
		raise
	xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
	return ok