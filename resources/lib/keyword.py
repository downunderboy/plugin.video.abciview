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

__addonid__ = 'plugin.video.abc_iview'
__settings__ = settings.Settings(__addonid__, sys.argv)
__fanart__ = __settings__.get_path('fanart.jpg')

BASE_SKIN_THUMBNAIL_PATH = __settings__.get_path('resources/media')
BASE_PLUGIN_THUMBNAIL_PATH = __settings__.get_path('resources/media')

def get_keyword(keyword):
	iview_config = comm.get_config()
	keyword = comm.get_keyword_items(iview_config, keyword)
	return keyword

def make_list(keyword):
	try:
		series = get_keyword(keyword)
		series.sort()

		# fill media list
		ok = fill_media_list(series)
	except:
		# oops print error message
		print "ERROR: %s (%d) - %s" % (sys.exc_info()[2].tb_frame.f_code.co_name, sys.exc_info()[2].tb_lineno, sys.exc_info()[1])
		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def fill_media_list(series_list):
	iview_config = comm.get_config()
	try:
		ok = True
		# enumerate through the list of categories and add the item to the media list
		for s in series_list:
			url = "%s?series_id=%s" % (sys.argv[0], s.id)
			thumbnail = get_thumbnail(s.id)
			if s.get_image() and len(s.get_image()) > 0:
				icon = s.get_image()
			else:
				icon = "defaultfolder.png"
			listitem = xbmcgui.ListItem(s.get_title(), iconImage=icon, thumbnailImage=icon)
			listitem.setProperty('fanart_image', icon)
			listitem.setInfo('video',{'episode':s.get_num_episodes(), 'plot': s.get_plot()})
			# add the item to the media list
			ok = xbmcplugin.addDirectoryItem(
						handle=int(sys.argv[1]), 
						url=url, 
						listitem=listitem, 
						isFolder=True, 
						totalItems=len(series_list)
					)
			# if user cancels, call raise to exit loop
			if (not ok): 
				raise
		xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		d.ok('ABC iView Error', 'ABC iView encountered an error:', '  %s (%d) - %s' % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ]) )
		return None

		# user cancelled dialog or an error occurred
		print "ERROR: %s (%d) - %s" % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
		ok = False
	return ok


def get_thumbnail(series_id):
	# create the full thumbnail path for skins directory
	thumbnail = xbmc.translatePath( os.path.join(BASE_SKIN_THUMBNAIL_PATH, series_id + ".tbn" ) )
	# use a plugin custom thumbnail if a custom skin thumbnail does not exists
	if ( not os.path.isfile(thumbnail) ):
		# create the full thumbnail path for plugin directory
		thumbnail = xbmc.translatePath( os.path.join(BASE_PLUGIN_THUMBNAIL_PATH, series_id + ".tbn" ) )
		# use a default thumbnail if a custom thumbnail does not exists
		if ( not os.path.isfile( thumbnail ) ):
			thumbnail = ""
	return thumbnail
