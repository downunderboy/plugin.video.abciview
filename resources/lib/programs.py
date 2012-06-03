import sys
import config
import utils
import comm
import os

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

def make_list(url):
	params = utils.get_url(url)	

	# Show a dialog
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('ABC iView', 'Getting Episode List')
	pDialog.update(50)

	programs = get_programs(params['series_id'])
	ok = fill_media_list(programs)

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)

def get_programs(series_id):
	iview_config = comm.get_config()
	return comm.get_series_items(iview_config, series_id)

def fill_media_list(programs):
	ok = True
	for p in programs:
		listitem=xbmcgui.ListItem(label=p.get_title(), iconImage=p.thumbnail, thumbnailImage=p.thumbnail)
		listitem.setInfo('video', p.get_xbmc_list_item())
		listitem.setProperty('fanart_image', p.thumbnail)

		# Build the URL for the program, including the list_info
		url = "%s?%s" % (sys.argv[0], p.make_xbmc_url())

		# Add the program item to the list
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)
		# if user cancels, call raise to exit loop
		if (not ok): 
			raise
	xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
	return ok
