import sys
import config
import utils
import comm
import os
import series
import xbmcsettings as settings

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

__addonid__ = 'plugin.video.abciview'
__settings__ = settings.Settings(__addonid__, sys.argv)
__fanart__ = __settings__.get_path('fanart.png')

def make_list(url):
	params = utils.get_url(url)	
	
	# Show a dialog
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('ABC iView', 'Getting Category List')
	pDialog.update(50)

	series_list = get_series_list(params["category"])
	series_list.sort()
	# fill media list
	ok = fill_media_list(series_list)

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)

def get_series_list(category):
	iview_config = comm.get_config()
	return comm.get_category_series(iview_config, category)

def fill_media_list(series_list):
	iview_config = comm.get_config()
	ok = True
	# enumerate through the list of categories and add the item to the media list
	xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
	for s in series_list:
		url = '%s?series_id=%s' % (sys.argv[0], s.id)
		thumbnail = ''
		icon = 'defaultfolder.png'
		if s.get_image() and len(s.get_image()) > 0:
			icon = thumbnail = s.get_image()
			__fanart__ = icon
		
		listitem = xbmcgui.ListItem(s.get_title(), iconImage=icon, thumbnailImage=thumbnail)
		listitem.setProperty('fanart_image', __fanart__)
		listitem.setInfo('video', {'episode':s.get_num_episodes(), 'plot': s.get_plot(), 'genre': s.get_keywords()})
		# add the item to the media list
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True, totalItems=len(series_list))
		# if user cancels, call raise to exit loop
		if (not ok):
			raise
	return ok
