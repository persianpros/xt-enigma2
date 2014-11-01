# -*- coding: utf-8 -*-
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import gettext

#def localeInit():
#	gettext.bindtextdomain("AtemioDeviceManager", resolveFilename(SCOPE_PLUGINS, "SystemPlugins/AtemioDeviceManager/locale"))

def _(txt):
	t = gettext.dgettext("AtemioDeviceManager", txt)
	if t == txt:
#		print "[AtemioDeviceManager] fallback to default translation for:", txt
		t = gettext.gettext(txt)
	return t

#localeInit()
#language.addCallback(localeInit)