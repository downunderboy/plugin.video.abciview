'''
	Plugin for streaming content from ABC's iView
'''
import os, sys, xbmcplugin, xbmcgui

import resources.lib.utils as utils
import resources.lib.series as series
import resources.lib.programs as programs
import resources.lib.play as play
import resources.lib.category as category
import resources.lib.keyword as keyword
import resources.lib.xbmcsettings as settings

# plugin constants
__plugin__  = 'ABC iView'
__author__  = 'Andy Botting, Brian Hornsby'
__credits__ = 'Team XBMC, Jeremy Visser, Noisymime'
__addonid__ = 'plugin.video.abc_iview'
__settings__ = settings.Settings(__addonid__, sys.argv)
__version__ = __settings__.get_version()
__fanart__ = os.path.join(__settings__.get_path(),'fanart.png')
xbmcplugin.setPluginFanart(int(__settings__.get_argv(1)), __fanart__)

print '[PLUGIN] %s: version %s initialized!' % (__plugin__, __version__)

def add_directory(title, key, id, icon='abc.png', fanart=None):
	url = '%s?%s=%s' % (sys.argv[0], key, id)
	icon = __settings__.get_path(('resources/images/%s' % icon))
	listitem = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
	if fanart != None and len(fanart) > 0:
		listitem.setProperty('fanart_image', __settings__.get_path(('resources/images/%s' % fanart)))
	else:	
		listitem.setProperty('fanart_image', __fanart__)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True)

def station_menu():
	add_directory('ABC 1', 'category', 'abc1', 'abc1.png', 'abc1bg.png')
	add_directory('ABC 2', 'category', 'abc2', 'abc2.png', 'abc2bg.png')
	add_directory('ABC 3', 'category', 'abc3', 'abc3.png', 'abc3bg.png')
	add_directory('ABC News 24', 'category', 'abc4', 'abc24.png', 'abc24bg.png')
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def genre_menu():
	add_directory('ABC 4 Kids', 'category', 'pre-school')
	add_directory('Arts & Culture', 'category', 'arts')
	add_directory('Comedy', 'category', 'comedy')
	add_directory('Documentary', 'category', 'docs')
	add_directory('Drama', 'category', 'drama')
	add_directory('Lifestyle', 'category', 'lifestyle')
	add_directory('News & Current Affairs', 'category', 'news')
	add_directory('Panel & Discussion', 'category', 'panel')
	add_directory('Sport', 'category', 'sport')
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

def root_menu():
	add_directory('Featured', 'root', 'featured')
	add_directory('Recently Added', 'root', 'recent')
	add_directory('Last Chance', 'root', 'last-chance')
	add_directory('Genre', 'root', 'genre')
	add_directory('Station', 'root', 'station')
	add_directory('A - Z Index', 'root', 'index')
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

if __name__ == '__main__':
	params_str = sys.argv[2]
	params = utils.get_url(params_str)

	if (len(params) == 0):
		root_menu()
	else:
		if params.has_key('series_id'):
			programs.make_list(params_str)
		elif params.has_key('title'):
			play.play(params_str)
		elif params.has_key('root'):
			if params['root'] == 'featured':
				keyword.make_list('featured')
			elif params['root'] == 'last-chance':
				keyword.make_list('last-chance')
			elif params['root'] == 'recent':
				keyword.make_list('recent')
			elif params['root'] == 'genre':
				genre_menu()
			elif params['root'] == 'station':
				station_menu()
			else:
				series.make_list()
		elif params.has_key('category'):
			category.make_list(params_str)
		else:
			series.make_list()
