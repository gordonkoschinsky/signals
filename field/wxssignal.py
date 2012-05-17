"""
A simple wx wrapper around a ssginal.py RPC signal server.
Flashes its background if the state is polled,
and shows red/green state as a circle
"""

import wx
import sys
import ssignal
import socket
import Pyro4
from pubsub import pub

class SsignalWrapper(ssignal.Signal):
    """
    A thin wrapper around ssignal.Signal
    Publishes a pubsub message in every method that is of interest for the GUI
    and calls the parent class' method afterwards
    """
    def __init__(*args, **kwargs):
        ssignal.Signal.__init__(*args, **kwargs)

    def getState(self):
        try:
            state = ssignal.Signal.getState(self)
        except Pyro4.errors.TimeoutError:
            pass
        wx.CallAfter(pub.sendMessage, "ssignal.stateRequested", state=state)
        return state

    def changeStateTo(self, state):
        state = ssignal.Signal.changeStateTo(self, state)
        wx.CallAfter(pub.sendMessage, "ssignal.stateChanged", state=state)
        return state

class SketchFrame(wx.Frame):
    def __init__(self, parent, title="Signal", signalName="S", **kwargs):
        x = kwargs.get('FrameX', 0)

        wx.Frame.__init__(self, parent=parent, id=wx.ID_ANY, title=title,size=(170,230), pos=(x,0))
        self.signalName = signalName
        self.adressString = "-.-.-.-:-"

        # COMMUNICATION
        self.signal = Pyro4.Proxy("PYRONAME:signal.{}".format(self.signalName))

        # WIDGETS
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.sketch = SketchWindow(self.panel)
        Hp0Button = wx.Button(self.panel, label="Set to Hp0")
        Ks1Button = wx.Button(self.panel, label="Set to Ks1")
        Ks2Button = wx.Button(self.panel, label="Set to Ks2")
        DisconnectButton = wx.Button(self.panel, label="Disconnect")


        # SIZERS
        topSizer = wx.BoxSizer(wx.VERTICAL)

        sketchSizer = wx.BoxSizer(wx.HORIZONTAL)
        sketchSizer.Add(self.sketch, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)

        buttonSizer = wx.GridSizer(2,2)
        buttonSizer.Add(Hp0Button)
        buttonSizer.Add(Ks1Button)
        buttonSizer.Add(Ks2Button)
        buttonSizer.Add(DisconnectButton)

        topSizer.Add(buttonSizer, flag=wx.ALL|wx.EXPAND, border=2)
        topSizer.Add(sketchSizer, proportion=1,flag=wx.ALL|wx.EXPAND)
        self.panel.SetSizer(topSizer)

        # EVENTS
        Hp0Button.Bind(wx.EVT_BUTTON, self.onSetHp0)
        Ks1Button.Bind(wx.EVT_BUTTON, self.onSetKs1)
        Ks2Button.Bind(wx.EVT_BUTTON, self.onSetKs2)
        DisconnectButton.Bind(wx.EVT_BUTTON, self.onDisconnect)

        pub.subscribe(self.onSignalStateRequested, "ssignal.stateRequested") # Received when the signal wrapper fires
        pub.subscribe(self.onSignalChange, "ssignal.stateChanged") # Received when the signal wrapper fires
        pub.subscribe(self.onDaemonAnnounced, "Signal.{}.daemon".format(signalName))

    def onSetHp0(self, event):
        self.signal.changeStateTo("Hp0")

    def onSetKs1(self, event):
        self.signal.changeStateTo("Ks1")

    def onSetKs2(self, event):
        self.signal.changeStateTo("Ks2")

    def onDisconnect(self, event):
        self.signal.daemonActive = False
        self.signal.disconnect()

    def onDaemonAnnounced(self, daemon):
        # This will be called from the signal thread.
        # To avoid thread conflicts, everything that is to do here is wrapped in
        # a callAfter() call.
        # it's not possible to do this in the Signal.__init__(), since
        # I want to keep wx stuff out of there.
        #
        def setAddressString(daemon):
            self.adressString = daemon.locationStr
            self.sketch.Refresh()

        wx.CallAfter(setAddressString, daemon)

    def onFlashBG(self, event):
        self.sketch.flashBG()

    def onSignalStateRequested(self, state):
        self.onSignalChange(state) # set the right color for the signal also

        self.sketch.flashBG()

    def onSignalChange(self, state):
        if state and state in self.sketch.statemap:
            self.sketch.signalState = state
        else:
            self.sketch.signalState = "off"

class SketchWindow(wx.Window):
    def __init__ (self, parent):
        wx.Window.__init__(self, parent)

        self.Buffer = None
        self.bgColor = wx.NullColor
        self.signalState = "off"

        darkgrey = wx.Colour(50,50,50)

        self.statemap = {}
        self.statemap["off"] = (darkgrey, darkgrey, darkgrey)
        self.statemap["Hp0"] = ('red',darkgrey, darkgrey)
        self.statemap["Ks1"] = (darkgrey, 'green', darkgrey)
        self.statemap["Ks2"] = (darkgrey, darkgrey, 'yellow')

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnPaint)
        #self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack)

    def flashBG(self):
        self.bgColor = "YELLOW"
        self.Refresh()
        wx.CallLater(100, self.resetBG)

    def resetBG(self):
        self.bgColor = wx.NullColor
        self.Refresh()

    def InitBuffer(self):
        size=self.GetClientSize()
        # if buffer exists and size hasn't changed do nothing
        if self.Buffer is not None and self.Buffer.GetWidth() == size.width and self.Buffer.GetHeight() == size.height:
            return False

        self.Buffer=wx.EmptyBitmap(size.width,size.height)
        dc=wx.MemoryDC()
        dc.SelectObject(self.Buffer)
        self.DrawSignal(dc)
        dc.SelectObject(wx.NullBitmap)
        return True

    def DrawSignal(self,dc):
        if self.bgColor:
            dc.SetBackground(wx.Brush(self.bgColor))
        else:
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        ws = 40
        hs = 75
        cs = 5
        dia = ws / 5

        size=self.GetClientSize()
        soffsetx = size.width/2-ws/2
        soffsety = 30

        # signal body
        pen=wx.Pen('black',4)
        dc.SetPen(pen)
        dc.SetBrush(wx.Brush('black'))

        dc.DrawPolygon(((0,cs),(0,hs),(ws,hs),(ws,cs),(ws-cs,0),(cs,0)), xoffset=soffsetx, yoffset=soffsety)

        # signal lights
        # top (red)
        dc.SetBrush(wx.Brush(self.statemap[self.signalState][0]))
        dc.DrawCircle(soffsetx+ws/2, soffsety+hs/4, dia)

        # bottom left (green)
        dc.SetBrush(wx.Brush(self.statemap[self.signalState][1]))
        dc.DrawCircle(soffsetx+ws/4, soffsety+hs/2, dia)

        # bottom right (yellow)
        dc.SetBrush(wx.Brush(self.statemap[self.signalState][2]))
        dc.DrawCircle(soffsetx+ws-ws/4, soffsety+hs/2, dia)


        # Signal Name
        dc.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        text = wx.GetApp().TopWindow.signalName
        textX,void,void,void = dc.GetFullTextExtent(text)
        dc.DrawText(text, size.width/2 - textX/2, 0)

        # Signal Address
        dc.SetFont(wx.Font(8, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        text = wx.GetApp().TopWindow.adressString
        textX,void,void,void = dc.GetFullTextExtent(text)
        dc.DrawText(text, size.width/2 - textX/2, size.height-15)


    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh() # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.DrawSignal(dc)



from threading import Thread, Event
from wx.lib.pubsub import Publisher
from pubsub import pub

class SsignalThread(Thread):
    """
    Puts ssignal.signal into a Thread, so the GUI won't block if the
    Pyro daemon starts its own main loop
    """
    def __init__(self, name, states, defaultState, host="localhost"):
        self.signalname = name
        self.states = states
        self.defaultState = defaultState
        self.host = host

        Thread.__init__(self)
        self.setDaemon(True)
        self.start()

    def run(self):
        SsignalWrapper(self.signalname, self.states, self.defaultState, self.host)



def createSignalRepresentation(name="S", host="localhost", **kwargs):
    app=wx.App(redirect=False)

    frame=SketchFrame(parent=None, title=name, signalName=name, adressString = "{}:{}".format(host,"?"), **kwargs)

    s = SsignalThread(name, ("Hp0","Ks1","Ks2"), "Hp0", host=host)

    frame.Show(True)
    frame.ToggleWindowStyle(wx.STAY_ON_TOP)

    app.MainLoop()


if __name__=='__main__':
    # test case
    import pyronameserver as pns
    ns = pns.startNameServer(Pyro4.socketutil.getMyIpAddress(workaround127=True))

    host = Pyro4.socketutil.getMyIpAddress(workaround127=True)
    Pyro4.config.COMMTIMEOUT = 5
    createSignalRepresentation("S1", host=host)
