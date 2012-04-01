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

__addonid__ = 'plugin.video.abc_iview'
__settings__ = settings.Settings(__addonid__, sys.argv)
__fanart__ = __settings__.get_path('fanart.jpg')

BASE_SKIN_THUMBNAIL_PATH = __settings__.get_path('resources/media')
BASE_PLUGIN_THUMBNAIL_PATH = __settings__.get_path('resources/media')

def make_list(url):
	params = utils.get_url(url)	
#	try:
	# Show a dialog
	pDialog = xbmcgui.DialogProgress()
	pDialog.create('ABC iView', 'Getting Category List')
	pDialog.update(50)

	series_list = get_series_list(params["category"])
	series_list.sort()
	# fill media list
	ok = fill_media_list(series_list)
		
#	except:
#		# oops print error message
#		print "ERROR: %s (%d) - %s" % (sys.exc_info()[2].tb_frame.f_code.co_name, sys.exc_info()[2].tb_lineno, sys.exc_info()[1])
#		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)

def get_series_list(category):
	iview_config = comm.get_config()
	return comm.get_category_series(iview_config, category)

def fill_media_list(series_list):
   iview_config = comm.get_config()
#   try:
   ok = True
   # enumerate through the list of categories and add the item to the media list
   xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
   for s in series_list:
      url = "%s?series_id=%s" % (sys.argv[0], s.id)
      thumbnail = get_thumbnail(s.id)
      icon = "defaultfolder.png"
      listitem = xbmcgui.ListItem(s.get_title(), iconImage=icon, thumbnailImage=thumbnail)
      listitem.setProperty('fanart_image', __fanart__)
      listitem.setInfo('video',{'episode':s.get_num_episodes()})
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
#   except:
#      # user cancelled dialog or an error occurred
#      d = xbmcgui.Dialog()
#      d.ok('ABC iView Error', 'ABC iView encountered an error:', '  %s (%d) - %s' % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ]) )
#      return None

  # user cancelled dialog or an error occurred
#   print "ERROR: %s (%d) - %s" % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
#   ok = False
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
