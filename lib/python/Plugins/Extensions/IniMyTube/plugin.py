from . import _

from Plugins.Plugin import PluginDescriptor
from MyTubeService import validate_cert
from enigma import eTPM
from Components.config import ConfigSubsection, config, ConfigYesNo

config.plugins.mytubestart = ConfigSubsection()
config.plugins.mytubestart.extmenu = ConfigYesNo(default=True)


def MyTubeMain(session, **kwargs):
	import ui
	session.open(ui.MyTubePlayerMainScreen,plugin_path)


def Plugins(path, **kwargs):
	global plugin_path
	plugin_path = path

	name=_("My TubePlayer")
	descr=_("Play YouTube movies")
	where = [PluginDescriptor.WHERE_PLUGINMENU,]
	if config.plugins.mytubestart.extmenu.value:
		where.append(PluginDescriptor.WHERE_EXTENSIONSMENU)
	return PluginDescriptor(name=name, description=descr, where=where, icon="plugin.png", fnc=MyTubeMain)
