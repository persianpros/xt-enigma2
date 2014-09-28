PANELVER = '1.0.0'
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from enigma import eTimer, eConsoleAppContainer
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List
from Components.ProgressBar import ProgressBar
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.PluginComponent import plugins
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN
from os import popen, system, remove, listdir, chdir, getcwd, statvfs, mkdir, path, walk
from Screens.NetworkSetup import *
#from Screens.PluginBrowser import *
#from Plugins.SystemPlugins.SoftwareManager.Flash_online import FlashOnline
from IPKInstaller import Ipkinstall
from Plugins.SystemPlugins.AtemioDeviceManager.HddSetup import *
from About import AboutTeam
import os
import sys
from Plugins.Plugin import PluginDescriptor
from Tools import Notifications

def GetSkinPath():
    myskinpath = resolveFilename(SCOPE_CURRENT_SKIN, '')
    myskinpath = '/usr/lib/enigma2/python/Plugins/Extensions/AtemioPanel/'
    return myskinpath

def getVarSpaceKb():
    try:
        s = statvfs('/')
    except OSError:
        return (0, 0)

    return (float(s.f_bfree * (s.f_bsize / 1024)), float(s.f_blocks * (s.f_bsize / 1024)))


class AtemioPanel(Screen):
	__module__ = __name__
	skin="""
		<screen name="Atemio Panel" position="center,center" size="800,600" title="Atemio Panel">
			<widget source="list" render="Listbox" position="15,80" size="730,500" scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{"template": [
									MultiContentEntryText(pos = (90, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),
									MultiContentEntryText(pos = (110, 30), size = (640, 50), font=0, flags = RT_VALIGN_TOP, text = 2),
									MultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(72, 72), png = 3),
								],
					"fonts": [gFont("Regular", 20)],
					"itemHeight": 80
					}
				</convert>
			</widget>
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/AtemioPanel/icons/logo.png" position="30,0" size="711,76" alphatest="on" />
			<widget source="conn" render="Label" position="15,540" size="730,35" font="Regular;20" halign="center" valign="center" transparent="1" />
		</screen>"""
    	
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = List(self.list)
		self['conn'] = StaticText('')
		self['spaceused'] = ProgressBar()

		self.MenuList = [('SoftCam',_('SoftCam Panel'),_('Configure and install softcams'),'icons/p_cam.png',fileExists('/usr/lib/enigma2/python/Plugins/Extensions/SoftCamPanel/plugin.pyo')),
			('Network',_('Network'),_('configure your network'),'icons/p_network.png',True),
			('AtemioIPKInstaller',_('Atemio IPK Installer'),_('install IPK from any device'),'icons/p_plugins.png',True),
			#('FlashOnline',_('Flash Image online'),_('Flash image online on the fly'),'icons/p_plugins.png',True),        
			('AtemioDevice',_('Atemio Device Manager'),_('Setup HDD / USB devices'),'icons/p_device.png', True),
			('Info',_('Info'),_('Show info'),'icons/p_about.png', True)]

		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], 
        	{
				'ok': self.KeyOk,
				'red': self.cancel,
				'back': self.cancel,
			},-1)
				
		self.onLayoutFinish.append(self.updateList)
		self.onShown.append(self.setWindowTitle)
        
	def ConvertSize(self, size):
		size = int(size)
		if size >= 1073741824:
			Size = '%0.2f TB' % (size / 1073741824.0)
		elif size >= 1048576:
			Size = '%0.2f GB' % (size / 1048576.0)
		elif size >= 1024:
			Size = '%0.2f MB' % (size / 1024.0)
		else:
			Size = '%0.2f KB' % size
		return str(Size)

	def setWindowTitle(self):
		diskSpace = getVarSpaceKb()
		percFree = int(diskSpace[0] / diskSpace[1] * 100)
		percUsed = int((diskSpace[1] - diskSpace[0]) / diskSpace[1] * 100)
		self.setTitle('%s - %s: %s (%d%%)' % (_('Atemio Panel'),
		 _('Free'),
		 self.ConvertSize(int(diskSpace[0])),
		 percFree))
		self['spaceused'].setValue(percUsed)

	def KeyOk(self):
		self['conn'].text = ''
		sel = self['list'].getCurrent()[0]
		if sel == 'SoftCam':
			from Plugins.Extensions.SoftCamPanel import SoftCamPanel
			self.session.open(SoftCamPanel.SoftCamPanel)
		elif sel == 'Network':
			self.session.open(NetworkAdapterSelection)
		elif sel == 'AtemioIPKInstaller':
			self.session.open(Ipkinstall)
		#elif sel == 'FlashOnline':
		#	self.session.open(FlashOnline)
		elif sel == 'AtemioDevice':
			self.session.open(HddSetup)
		elif sel == 'Info':
			self.session.open(AboutTeam)

	def cancel(self):
		self.close()

	def updateList(self):
		del self.list[:]
		skin_path = GetSkinPath()
		for i in self.MenuList:
			if i[4]:
				self.list.append((i[0],
				 i[1],
				 i[2],
				 LoadPixmap(skin_path + i[3])))

		self['list'].setList(self.list)

def main(session, **kwargs):
    session.open(AtemioPanel)


def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Atemio Panel'),
          main,
          'Atemio_mainmenu',
          44)]
    return []


def Plugins(**kwargs):
    list = []
    list.append(PluginDescriptor(icon='icons/icon.png', name='Atemio Panel', description='Atemio Panel', where=PluginDescriptor.WHERE_MENU, fnc=menu))
    return list