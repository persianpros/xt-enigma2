# for localized messages
from . import _

from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigBoolean
from Components.Harddisk import harddiskmanager
from Plugins.Extensions.AtemioPanel.BackupManager import BackupManagerautostart
from Plugins.Extensions.AtemioPanel.ImageManager import ImageManagerautostart
from Plugins.Extensions.AtemioPanel.IPKInstaller import IpkgInstaller

from os import path, listdir

def checkConfigBackup():
	try:
		devices = [(r.description, r.mountpoint) for r in harddiskmanager.getMountedPartitions(onlyhotplug = False)]
		list = []
		files = []
		for x in devices:
			if x[1] == '/':
				devices.remove(x)
		if len(devices):
			for x in devices:
				devpath = path.join(x[1],'backup')
				if path.exists(devpath):
					try:
						files = listdir(devpath)
					except:
						files = []
				else:
					files = []
				if len(files):
					for file in files:
						if file.endswith('.tar.gz'):
							list.append((path.join(devpath,file),devpath,file))
		if len(list):
			return True
		else:
			return None
	except IOError, e:
		print "unable to use device (%s)..." % str(e)
		return None

if checkConfigBackup() is None:
	backupAvailable = 0
else:
	backupAvailable = 1

def AtemioSoftwareManager(session):
	import ui
	return ui.AtemioSoftwareManager(session)

def UpgradeMain(session, **kwargs):
	session.open(AtemioSoftwareManager)

def startSetup(menuid):
	if menuid != "setup":
		return [ ]
	return [(_("Atemio"), UpgradeMain, "Atemio_menu", 1010)]

config.misc.restorewizardrun = ConfigBoolean(default = False)
def AtemioRestoreWizard(*args, **kwargs):
	from Plugins.Extensions.AtemioPanel.AtemioRestoreWizard import AtemioRestoreWizard
	return AtemioRestoreWizard(*args, **kwargs)

def BackupManager(session):
	from Plugins.Extensions.AtemioPanel.BackupManager import AtemioBackupManager
	return AtemioBackupManager(session)
def BackupManagerMenu(session, **kwargs):
	session.open(AtemioBackupManager)

def AtemioImageManager(session):
	from Plugins.Extensions.AtemioPanel.ImageManager import AtemioImageManager
	return AtemioImageManager(session)
def ImageMangerMenu(session, **kwargs):
	session.open(AtemioImageManager)

def filescan_open(list, session, **kwargs):
	filelist = [x.path for x in list]
	session.open(IpkgInstaller, filelist) # list

def filescan(**kwargs):
	from Components.Scanner import Scanner, ScanPath
	return \
		Scanner(mimetypes = ["application/x-debian-package"],
			paths_to_scan =
				[
					ScanPath(path = "ipk", with_subdirs = True),
					ScanPath(path = "", with_subdirs = False),
				],
			name = "Ipkg",
			description = _("Install extensions."),
			openfnc = filescan_open, )

def Plugins(path, **kwargs):
	plist = [PluginDescriptor(where=PluginDescriptor.WHERE_ATEMIOSOFTWAREMANAGER, needsRestart = False, fnc=startSetup)]
	plist.append(PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = ImageManagerautostart))
	plist.append(PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = BackupManagerautostart))
	
	if config.misc.firstrun.value and not config.misc.restorewizardrun.value and backupAvailable == 1:
		plist.append(PluginDescriptor(name=_("Restore Wizard"), where = PluginDescriptor.WHERE_WIZARD, needsRestart = False, fnc=(3, AtemioRestoreWizard)))

	plist.append(PluginDescriptor(name=_("Ipkg"), where = PluginDescriptor.WHERE_FILESCAN, needsRestart = False, fnc = filescan))

	
	return plist