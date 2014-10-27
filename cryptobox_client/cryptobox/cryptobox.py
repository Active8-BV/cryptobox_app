import os
import wx
from wx import adv
from wx import Icon

# #######################################################################

import os, sys, inspect


def get_base_dir():
    """
    get_base_dir
    """
    if getattr(sys, "frozen", False):
        # If this is running in the context of a frozen (executable) file,
        # we return the path of the main application executable
        return os.path.dirname(os.path.dirname(os.path.abspath(sys.executable)))
    else:
        # If we are running in script or debug mode, we need
        # to inspect the currently executing frame. This enable us to always
        # derive the directory of main.py no matter from where this function
        # is being called
        thisdir = inspect.getfile(inspect.currentframe())
        return os.path.abspath(os.path.join(thisdir, os.pardir))


class MailIcon(adv.TaskBarIcon):
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE = wx.NewId()
    TBMENU_CHANGE = wx.NewId()
    TBMENU_REMOVE = wx.NewId()

    def __init__(self, frame):
        """
        @type frame: str, unicode
        @return: None
        """
        adv.TaskBarIcon.__init__(self)
        self.frame = frame

        # Set the image
        icon = Icon()
        icon.CopyFromBitmap(wx.Bitmap(os.path.join(get_base_dir(), "Resources/traybar.png"), wx.BITMAP_TYPE_PNG))
        self.tbIcon = icon
        self.SetIcon(self.tbIcon, "Cryptobox")

        # bind some evts
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)
        self.Bind(adv.EVT_TASKBAR_LEFT_DOWN, self.OnTaskBarLeftClick)

    def CreatePopupMenu(self, evt=None):
        """
        This method is called by the base class when it needs to popup
        the menu for the default EVT_RIGHT_DOWN evt.  Just create
        the menu how you want it and return it from this function,
        the base class takes care of the rest.
        """
        menu = wx.Menu()
        menu.Append(self.TBMENU_RESTORE, "Open Program")
        menu.Append(self.TBMENU_CHANGE, "Show all the Items")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE, "Exit Program")
        return menu

    def OnTaskBarActivate(self, evt):
        """"""
        pass

    def OnTaskBarClose(self, evt):
        """
        Destroy the taskbar icon and frame from the taskbar icon itself
        """
        self.frame.Close()

    def OnTaskBarLeftClick(self, evt):
        """
        Create the right-click menu
        """
        menu = self.tbIcon.CreatePopupMenu()
        self.PopupMenu(menu)
        menu.Destroy()

########################################################################


class CryptoboxForm(wx.Frame):

    def __init__(self):
        """
        __init__
        """
        wx.Frame.__init__(self, None, wx.ID_ANY, "Cryptobox", size=(640, 480))
        panel = wx.Panel(self)
        self.tbIcon = MailIcon(self)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self._SetupMenus()

    def _SetupMenus(self):
        """Make the frames menus"""
        menub = wx.MenuBar()

        for x in menub.OSXGetAppleMenu().GetMenuItems():

            if 5006 != x.GetId():
                menub.OSXGetAppleMenu().DestroyItem(x.GetId())
        fmenu = wx.Menu()
        #fmenu.Append(wx.ID_OPEN, "Open\tCtrl+O")
        #fmenu.AppendSeparator()
        #fmenu.Append(wx.ID_SAVE, "Save\tCtrl+S")
        #fmenu.Append(wx.ID_SAVEAS, "Save As\tCtrl+Shift+S")
        #fmenu.AppendSeparator()
        #fmenu.Append(wx.ID_EXIT, "Exit\tCtrl+Q")
        #menub.Append(fmenu, "File")

        self.SetMenuBar(menub)

    def onClose(self, evt):
        """
        Destroy the taskbar icon and the frame
        """
        self.tbIcon.RemoveIcon()
        self.tbIcon.Destroy()
        self.Destroy()

# Run the program


if __name__ == "__main__":
    app = wx.App(False)
    frame = CryptoboxForm().Show()
    app.MainLoop()
