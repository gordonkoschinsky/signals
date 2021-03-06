import wx
import gui_raildiagram
import gui_statusbar

import logging
from wxLogHandler import WxLogHandler

import interlockingcom

from threadsafepub import pub as tpub

import Pyro4
Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800, 500))

        # WIDGETS
        self.panel = wx.Panel(self)

        logArea = wx.TextCtrl(self.panel,
                              style=\
                              wx.TE_MULTILINE |
                              wx.TE_READONLY |
                              wx.TE_RICH2)
        railDiagram = gui_raildiagram.RailDiagram(self.panel)

        button_S1green = wx.Button(self.panel, label="S1 Ks1")
        button_S1reset = wx.Button(self.panel, label="S1 Try Reset")

        self.sb = gui_statusbar.SwitchboardStatusBar(parent=self, fieldCount=3)
        self.SetStatusBar(self.sb)

        # SIZERS
        topSizer = wx.BoxSizer(wx.VERTICAL)

        bagSizer = wx.GridBagSizer()
        bagSizer.Add(logArea, pos=(0, 0), span=(6, 3), flag=wx.EXPAND | wx.ALL)
        bagSizer.Add(button_S1green, pos=(0, 3))
        bagSizer.Add(button_S1reset, pos=(1, 3))
        bagSizer.Add(railDiagram, pos=(6, 0), span=(12, 3), flag=wx.EXPAND | wx.ALL)
        bagSizer.AddGrowableCol(2)
        bagSizer.AddGrowableRow(1)

        topSizer.Add(bagSizer, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)
        self.panel.SetSizer(topSizer)

        # SETUP
        self.initLogging(logArea)

        # EVENTS
        button_S1green.Bind(wx.EVT_BUTTON, self.onS1green)
        button_S1reset.Bind(wx.EVT_BUTTON, self.onS1reset)
        self.Bind(wx.EVT_IDLE, self.onIdle)

        self.panel.Layout()
        self.Show()

        #self.logArea.SetDefaultStyle(wx.TextAttr(wx.RED))
        #self.logArea.AppendText("red?")
        #self.logArea.SetDefaultStyle(wx.TextAttr(wx.BLACK))

    def initLogging(self, logCtrl):
        rootLogger = logging.getLogger('')
        rootLogger.setLevel(logging.DEBUG)
        handler = WxLogHandler(logCtrl)
        handler.setFormatter(logging.Formatter('%(levelname)s | %(name)s | %(message)s [@ %(asctime)s in %(filename)s:%(lineno)d]'))
        rootLogger.addHandler(handler)
        #rootLogger.debug("Logging initialized")

    def onS1green(self, event):
        interlockingcom.sendMessage("signal.S1.requestKs1")

    def onS1reset(self, event):
        interlockingcom.sendMessage("signal.S1.requestReset")

    def onIdle(self, event):
        #logging.debug("IDLE")
        tpub.poll()

app = wx.App(redirect=0)

frame = MainFrame(None, 'Signals')

app.MainLoop()
