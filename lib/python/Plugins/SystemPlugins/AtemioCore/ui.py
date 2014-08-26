# for localized messages
from . import _

from Screens.Screen import Screen
from Components.ActionMap import NumberActionMap
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Components.MultiContent import MultiContentEntryText
from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER, gFont
from os import listdir, path, mkdir

class AtemioMenuBk(Screen):
	skin = """
	  <screen position="0,0" size="1401,721">
	  <widget font="Regular; 150" position="20,552" render="Label" size="1273,296" source="title" transparent="1" valign="top" zPosition="-50" />
	  <eLabel name="" position="606,92" size="525,547" zPosition="-11" />
	  <eLabel name="" position="0,0" size="1281,50" zPosition="-11" />
	  <widget font="Regular; 22" halign="left" position="258,10" render="Label" size="160,30" source="key_red" transparent="1" zPosition="1" />
	  <widget enableWrapAround="1" position="596,107" render="Listbox" scrollbarMode="showNever" size="547,513" source="menu" transparent="1">
	    <convert type="TemplatedMultiContent">
	  					{"template": [ MultiContentEntryText(pos = (30, 5), size = (420, 50), flags = RT_HALIGN_LEFT, text = 1) ],
	  					"fonts": [gFont("Regular", 30)],
	  					"itemHeight": 60
	  					}
	  				</convert>
	  </widget>
	  <widget position="655,481" render="Listbox" scrollbarMode="showNever" selectionDisabled="1" size="392,125" source="menu" transparent="1">
	    <convert type="TemplatedMultiContent">
	  	    {"template": [
	  	    MultiContentEntryText(pos = (0,0),size = (390,125),flags = RT_HALIGN_CENTER|RT_VALIGN_BOTTOM|RT_WRAP,text = 2),# index 0 is the MenuText,
	  	                 ],
	  	        "fonts": [gFont("Regular",20)],
	  	        "itemHeight": 125
	  	    }
	  	  </convert>
	  </widget>
	</screen>"""
	
	def __init__(self, session, args = 0):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Atemio"))
		self.menu = args
		self.list = []
		if self.menu == 0:
			self.list.append(("backup-manager", _("Backup Setting Manager"), _("Manage your backups of your settings." ), None))
			self.list.append(("image-manager", _("Backup Image Manager"), _("Create and Restore complete images of the system." ), None))
		self["menu"] = List(self.list)
		self["key_red"] = Button(_("Cancel"))

		self["shortcuts"] = NumberActionMap(["ShortcutActions", "WizardActions", "InfobarEPGActions", "MenuActions", "NumberActions"],
		{
			"ok": self.go,
			"red": self.close,
			"back": self.close,
		}, -1)
		self.onLayoutFinish.append(self.layoutFinished)
		self.onChangedEntry = []
		self["menu"].onSelectionChanged.append(self.selectionChanged)

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary
		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["menu"].getCurrent()
		if item:
			name = item[1]
			desc = item[2]
		else:
			name = "-"
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def layoutFinished(self):
		idx = 0
		self["menu"].index = idx

	def setWindowTitle(self):
		self.setTitle(_("Atemio"))

	def go(self, num = None):
		if num is not None:
			num -= 1
			if not num < self["menu"].count():
				return
			self["menu"].setIndex(num)
		current = self["menu"].getCurrent()
		if current:
			currentEntry = current[0]
			if self.menu == 0:
				if (currentEntry == "backup-manager"):
					from Plugins.Extensions.AtemioPanel.BackupManager import AtemioBackupManager
					self.session.open(AtemioBackupManager)
				elif (currentEntry == "image-manager"):
					from Plugins.Extensions.AtemioPanel.ImageManager import AtemioImageManager
					self.session.open(AtemioImageManager)
