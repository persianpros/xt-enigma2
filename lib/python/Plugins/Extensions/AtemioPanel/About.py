from enigma import *
from Screens.Screen import Screen
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap

class AboutTeam(Screen):
    skin = """
    <screen name="AboutTeam" position="0,0" size="1280,720" title="About Team" flags="wfNoBorder" >
        <panel name="GenericLayoutLiteTemplate" /> 
        <widget name="about" font="Regular;24" position="65,80" size="680,490" halign="center" transparent="1" backgroundColor="background" />
    </screen>"""

    def __init__(self, session, args = 0):
        Screen.__init__(self, session)
        abouttxt = '\nAtemio4you Image Team:\n\n- ch3wb4kka (Developer)\n- satinfo (Developer)\n- skaman (Developer)\n- mmark (Graphics and Skin) \n\n-Betatesting:\n xionsenx, volatile, master\n\nFurther credits goes to:\n- Atemio4You Team\n- ProjectMan for his great support\n\n- OE-Alliance, openViX, openPLi'
        self['about'] = Label(abouttxt)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'cancel': self.quit}, -2)

    def quit(self):
        self.close()
