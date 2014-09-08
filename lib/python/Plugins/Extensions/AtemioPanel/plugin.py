PANELVER = '0.1.0'
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens.PluginBrowser import *
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
import os
import sys
from Plugins.Plugin import PluginDescriptor
from Tools import Notifications
import xml.etree.cElementTree as x

from AtemioDownloader import AtemioDownloader, AtemioConsole
from About import AtemioUtils
t = AtemioUtils()

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


class util:
	
	pluginIndex = -1
	pluginType = ''
	typeDownload = 'A'
	addonsName = ''
	filename = ''
	dir = ''
	size = 0
	check = 0

u = util()

class loadXml:
	
	tree_list = []
	plugin_list = []
	
	def load(self,filename):
		del self.tree_list[:]
		del self.plugin_list[:]
		tree = x.parse(filename)
		root = tree.getroot()
		c = 0
		for tag in root.getchildren(): 
			self.tree_list.append([c, tag.tag])
			c1 = 0
			for b in tree.find(tag.tag):
				self.plugin_list.append([c,tag.tag,b.find("Filename").text,b.find("Descr").text,b.find("Folder").text,b.find("Size").text,b.find("Check").text,c1])
				c1 +=1
			c +=1

loadxml = loadXml()


class AtemioMenu(Screen):
    __module__ = __name__
    skin = """
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
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)

        self.MenuList = [('SoftCam',_('SoftCam Panel'),_('Configure your softcams'),'icons/p_cam.png',fileExists('/usr/lib/enigma2/python/Plugins/Extensions/SoftCamPanel/plugin.pyo')),
         ('PluginBrowser',_('Plugin Browser'),_('Install and remove plugins'),'icons/p_downloads.png',True),
         ('IPKInstall',_('IPK Installer'),_('Install local ipk files'),'icons/p_manual.png',True),
         ('MountManager',_('Mount Manager'),_('Mount or umount your device'),'icons/p_mount.png',True),         
         ('SwapManager',_('Swap Manager'),_('Added or remove swap'),'icons/p_swap.png',True),         
         ('ScriptEx',_('Script Executer'),_('Execute script'),'icons/p_script.png', True),
         ('Backup',_('Backup Atemio'),_('Backup setting and flash'),'icons/p_backup.png', True),
         ('aboutTeam',_('About Team'),_('Show info about Team'),'icons/p_about.png', True)]

        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'red': self.cancel,
         'back': self.cancel})
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
        if not self.container.running():
            sel = self['list'].getCurrent()[0]
            if sel == 'SoftCam':
                from Plugins.Extensions.SoftCamPanel import SoftCamPanel
                self.session.open(SoftCamPanel.SoftCamPanel)
            elif sel == 'PluginBrowser':
                self.session.open(PluginBrowser)
            elif sel == 'IPKInstall':
                from IPKInstaller import AtemioIPKInstaller
                self.session.open(AtemioIPKInstaller)
            elif sel == 'MountManager':
                from DeviceMount import DevicesPanel
                self.session.open(DevicesPanel)
            elif sel == 'SwapManager':
                from SwapManager import AtemioSwapPanel
                self.session.open(AtemioSwapPanel)
            elif sel == 'ScriptEx':
                self.session.open(ScriptExecuter)
            elif sel == 'aboutTeam':
                from About import AboutTeam
                self.session.open(AboutTeam)
            elif sel == 'Backup':
                from Plugins.SystemPlugins.AtemioCore.ui import AtemioMenuBk
                self.session.open(AtemioMenuBk)

    def runFinished(self, retval):
        if fileExists('/tmp/addons.xml'):
            try:
                loadxml.load('/tmp/addons.xml')
                remove('/tmp/addons.xml')
                self['conn'].text = ''
                self.session.open(AtemioExtraFile)
            except:
                self['conn'].text = _('File xml is not correctly formatted!')

        else:
            self['conn'].text = _('Server not found! Please check internet connection.')

    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            if self.container.running():
                self.container.kill()
            if fileExists('/tmp/addons.xml'):
                remove('/tmp/addons.xml')
            if fileExists('/tmp/tmp.tmp'):
                remove('/tmp/tmp.tmp')
            self['conn'].text = _('Process Killed by user. Server Not Connected!')

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

    def PluginDownloadBrowserClosed(self):
        self.updateList()

class ScriptExecuter(Screen):
    skin = """
    	<screen name="Script Panel" position="center,center" size="800,600">
    		<widget source="list" render="Listbox" position="14,10" size="770,491" scrollbarMode="showOnDemand">
    			<convert type="StringList" />
    		</widget>
    		<widget name="labstatus" position="14,510" size="800,30" font="Regular;21" valign="center" noWrap="1" backgroundColor="#333f3f3f" foregroundColor="#FFC000" shadowOffset="-2,-2" shadowColor="black" transparent="1" />
    		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/AtemioPanel/buttons/key_red.png" position="275,550" size="34,47" alphatest="on" />
    		<widget name="key_red" position="311,553" zPosition="1" size="209,40" font="Regular;20" halign="center" valign="center" backgroundColor="#009f1313" transparent="1" />
    	</screen>"""
    	
    def __init__(self, session):
        Screen.__init__(self, session)
        self['labstatus'] = Label(_('NO SCRIPT FOUND'))
        self['key_red'] = Label(_('Execute'))
        self.mlist = []
        self.populateScript()
        self['list'] = List(self.mlist)
        self['list'].onSelectionChanged.append(self.schanged)
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.startScript,
         'back': self.close,
         'red': self.startScript})
        self.onLayoutFinish.append(self.script_sel)
        self.onShown.append(self.setWindowTitle)

    def setWindowTitle(self):
        self.setTitle(_('Atemio Script Panel'))

    def script_sel(self):
        self['list'].index = 1
        self['list'].index = 0

    def populateScript(self):
        try:
            if not path.exists('/usr/script'):
                mkdir('/usr/script', 493)
        except:
            pass

        myscripts = listdir('/usr/script')
        for fil in myscripts:
            if fil.find('.sh') != -1:
                fil2 = fil[:-3]
                desc = 'N/A'
                f = open('/usr/script/' + fil, 'r')
                for line in f.readlines():
                    if line.find('#DESCRIPTION=') != -1:
                        line = line.strip()
                        desc = line[13:]

                f.close()
                res = (fil2, desc)
                self.mlist.append(res)

    def schanged(self):
        mysel = self['list'].getCurrent()
        if mysel:
            mytext = ' ' + mysel[1]
            self['labstatus'].setText(mytext)

    def startScript(self):
        mysel = self['list'].getCurrent()
        if mysel:
            mysel = mysel[0]
            mysel2 = '/usr/script/' + mysel + '.sh'
            mytitle = 'Atemio Script: ' + mysel
            self.session.open(Console, title=mytitle, cmdlist=[mysel2])


class	AtemioExtraFile(Screen):
	__module__ = __name__
	skin = """
	<screen position="center,center" size="634,474" >
		<widget source="list" render="Listbox" position="12,6" size="611,386" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
					{"template": [
							MultiContentEntryText(pos = (5, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),
							],
					"fonts": [gFont("Regular", 20)],
					"itemHeight": 36
					}
			</convert>
		</widget>
	  <ePixmap position="115,419" size="140,40" pixmap="skin_default/buttons/red.png" alphatest="on" />
	  <ePixmap position="414,416" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="on" />
	  <widget name="key_red" position="112,418" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
	  <widget name="key_green" position="416,417" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" /> 
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = List(self.list)
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Continue"))
		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			'back': self.close,
			'red': self.close,
			'green': self.KeyOk,
			
		})
		self.onLayoutFinish.append(self.loadData)
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(self.title)

	def KeyOk(self):
		u.pluginType = self["list"].getCurrent()[0]
		u.pluginIndex = self['list'].getIndex()
		self.session.open(AtemioExtraDown)

	def loadData(self):
		del self.list[:]
		for tag in loadxml.tree_list: 
			self.list.append((tag [1], tag [1]))
		self['list'].setList(self.list)


class	AtemioExtraDown(Screen):
	__module__ = __name__
	skin = """
	<screen position="center,center" size="560,530">
		<widget source="list" render="Listbox" position="17,6" size="540,416" scrollbarMode="showOnDemand">
			<convert type="TemplatedMultiContent">
						{"template": [
								MultiContentEntryText(pos = (5, 0), size = (530, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),
								],
						"fonts": [gFont("Regular", 20)],
						"itemHeight": 30
						}
			</convert>
		</widget>
		<widget source="conn" render="Label" position="16,425" size="540,55" font="Regular;20" halign="center" valign="center" transparent="1" />
		<ePixmap pixmap="skin_default/buttons/red.png" position="210,491" size="140,40" alphatest="on" />
	  <widget name="key_red" position="112,418" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
	  <widget name="key_green" position="416,417" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" /> 
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		self['list'] = List(self.list)
		self['conn'] = StaticText(_("Loading elements.\nPlease wait..."))
		self['type'] = Label("")
		self["key_red"] = Label(_("Cancel"))
		self["key_green"] = Label(_("Continue"))
		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.runFinished)
		self['type'].setText(_("Download ") + str(u.pluginType))

		self.linkExtra = t.readExtraUrl()

		self['actions'] = ActionMap(['WizardActions','ColorActions'],
		{
			'ok': self.KeyOk,
			'back': self.cancel,
			'red': self.cancel,
			'green': self.KeyOk,
		})
		self.onLayoutFinish.append(self.loadPlugin)
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("Atemio Panel Download ") + str(u.pluginType))

	def KeyOk(self):
		if not self.container.running():
			self.sel = self['list'].getIndex() 
			for tag in loadxml.plugin_list: 
				if tag [0] == u.pluginIndex:
					if tag [7] == self.sel:
						u.addonsName = tag [3]
						self.downloadAddons()
						return
			self.close()

	def loadPlugin(self):
		del self.list[:]
		for tag in loadxml.plugin_list: 
			if tag [0] == u.pluginIndex:
				self.list.append((tag [3], tag [3]))
		self['list'].setList(self.list)
		self['conn'].text = _('Elements Loaded!. Please select one to install.')

	def downloadAddons(self):
		self.getAddonsPar()
		if int(u.size) > int(t.getVarSpaceKb()[0]) and int(u.check) != 0:
			msg = _('Not enough space!\nPlease delete addons before install new.')
			self.session.open(MessageBox, msg , MessageBox.TYPE_INFO)
			return
		url = {'E':self.linkExtra}[u.typeDownload] + u.dir + "/" + u.filename 
		self.session.openWithCallback(self.executedScript, AtemioDownloader, url, "/tmp/", u.filename)

	def executedScript(self, *answer):
		if answer[0] == AtemioConsole.EVENT_DONE:
			if fileExists('/tmp/' + u.filename):
				msg = _('Do you want install the addon:\n%s?') % u.addonsName
				box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
				box.setTitle(_('Install Addon'))
			else:
				msg = _('File: %s not found!\nPlease check your internet connection.') % u.filename
				self.session.open(MessageBox, msg , MessageBox.TYPE_INFO)
		elif answer[0] == AtemioConsole.EVENT_KILLED:
			self['conn'].text = _('Process Killed by user!\nAddon not downloaded.')

	def installAddons(self, answer):
		if (answer is True):
			if (u.filename.find('.ipk') != -1):
				dest = "/tmp/" + u.filename
				mydir = getcwd()
				chdir("/")
				cmd = "opkg install " + dest
				cmd2 = "rm -f " + dest
				self.session.open(Console, title=_("Ipk Package Installation"), cmdlist=[cmd, cmd2])
				chdir(mydir)
				self['conn'].text = (_('Addon installed succesfully!'))
			elif (u.filename.find('.tbz') != -1):	
				self.container.execute("tar -xjvf /tmp/" + u.filename + " -C /")
				self['conn'].text = _('Please wait..Installing!')
			elif (u.filename.find('.tar.gz') != -1):	
				self.container.execute("tar -xzvf /tmp/" + u.filename + " -C /")
				self['conn'].text = _('Please wait..Installing!')
			elif (u.filename.find('.tgz') != -1):	
				self.container.execute("tar -xzvf /tmp/" + u.filename + " -C /")
				self['conn'].text = _('Please wait..Installing!')
			else:
				self['conn'].text = _('File: %s\nis not a valid package!') % u.filename
		else:
			if fileExists('/tmp/' + u.filename):
				remove("/tmp/" + u.filename)

	def runFinished(self, retval):
		if fileExists('/tmp/' + u.filename):
			remove("/tmp/" + u.filename)
		self['conn'].text = _("Addon installed succesfully!")
		if (u.pluginType == 'Plugins') or (u.pluginType == 'Plugin'):
			self['conn'].text = _("Reload Plugins list\nPlease Wait...")
			plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
			self['conn'].text = _("Addon installed succesfully!")
			msg = _("Enigma2 will be now hard restarted to complete package installation.") + "\n" + _("Do you want restart enigma2 now?")
			box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg , MessageBox.TYPE_YESNO)
			box.setTitle(_('Restart Enigma2'))
		
	def cancel(self):
		if not self.container.running():
			del self.container.appClosed[:]
			del self.container
			self.close()
		else:
			self.container.kill()
			self['conn'].text = _('Process Killed by user.\nAddon not installed correctly!')

	def restartEnigma2(self, answer):
		if (answer is True):
			system('killall -9 enigma2')

	def getAddonsPar(self):
		for tag in loadxml.plugin_list: 
			if tag [0] == u.pluginIndex:
				if tag [3] == u.addonsName:
					u.filename  = tag [2] 
					u.dir  = tag [4] 
					u.size  = tag [5] 
					u.check  = tag [6]

def main(session, **kwargs):
    session.open(AtemioMenu)


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
