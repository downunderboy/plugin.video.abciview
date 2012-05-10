"""
	Category module: fetches a list of categories to use as folders
"""

# main imports
import sys, os, re, urllib2, urllib
import xbmcsettings as settings
import comm

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

__addonid__ = 'plugin.video.abciview'
__settings__ = settings.Settings(__addonid__, sys.argv)

def get_series():
	iview_config = comm.get_config()
	programme = comm.get_programme(iview_config)
	return programme

def make_list():
	series = get_series()
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
		thumbnail = ''
		icon = 'defaultfolder.png'
		if s.get_image() and len(s.get_image()) > 0:
			icon = thumbnail = s.get_image()
			__fanart__ = icon
		else:
			__fanart__ = os.path.join(__settings__.get_path(),'fanart.png')
		
		listitem = xbmcgui.ListItem(s.get_title())
		listitem.setProperty('fanart_image', __fanart__)
		listitem.setInfo('video', {'episode':s.get_num_episodes(), 'plot': s.get_plot(), 'genre': s.get_keywords()})
		# add the item to the media list
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True, totalItems=len(series_list))
		# if user cancels, call raise to exit loop
		if (not ok): 
			raise
	xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
	return ok