"""
A simple wx wrapper around a ssginal.py RPC signal server.
Flashes its background if the state is polled,
and shows red/green state as a circle
"""

import wx
import sys
import ssignal
import socket

class SsignalWrapper(ssignal.Signal):
    """
    A thin wrapper around ssignal.Signal
    Publishes a pubsub message in every method that is of interest for the GUI
    and calls the parent class' method afterwards
    """
    def __init__(*args, **kwargs):
        ssignal.Signal.__init__(*args, **kwargs)

    def getState(self):
        state = ssignal.Signal.getState(self)
        wx.CallAfter(Publisher().sendMessage, "ssignal.stateRequested", state)
        return state

    def changeStateTo(self, state):
        state = ssignal.Signal.changeStateTo(self, state)
        wx.CallAfter(Publisher().sendMessage, "ssignal.stateChanged", state)
        return state

class SketchFrame(wx.Frame):
    def __init__(self, parent, title="Signal", signalName="S", adressString=""):
        wx.Frame.__init__(self, parent=parent, id=wx.ID_ANY, title=title,size=(140,250))
        self.signalName = signalName
        self.adressString = adressString

        # WIDGETS
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.sketch = SketchWindow(self.panel)
        testButton = wx.Button(self.panel, label="Test Signal Flash")

        # SIZERS
        topSizer = wx.BoxSizer(wx.VERTICAL)

        sketchSizer = wx.BoxSizer(wx.HORIZONTAL)
        sketchSizer.Add(self.sketch, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)

        topSizer.Add(testButton, flag=wx.ALL|wx.EXPAND, border=5)
        topSizer.Add(sketchSizer, proportion=1,flag=wx.ALL|wx.EXPAND)
        self.panel.SetSizer(topSizer)

        # EVENTS
        testButton.Bind(wx.EVT_BUTTON, self.onFlashBG)
        Publisher().subscribe(self.onSignalStateRequested, "ssignal.stateRequested") # Received when the signal wrapper fires
        Publisher().subscribe(self.onSignalChange, "ssignal.stateChanged") # Received when the signal wrapper fires


    def onFlashBG(self, event):
        self.sketch.flashBG()

    def onSignalStateRequested(self, message):
        self.onSignalChange(message) # set the right color for the signal also

        self.sketch.flashBG()

    def onSignalChange(self, message):
        if message.data:
            self.sketch.signalColor = message.data
        else:
            self.sketch.signalColor = wx.NullColor

class SketchWindow(wx.Window):
    def __init__ (self, parent):
        wx.Window.__init__(self, parent)

        self.Buffer = None
        self.bgColor = wx.NullColor
        self.signalColor = "BLACK" # default to black signal if we didn't get any state message yet

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack)

    def flashBG(self):
        self.Buffer = None  # delete the prepared buffer to redraw with new bg
        self.bgColor = "YELLOW"
        self.Refresh()
        wx.CallLater(100, self.resetBG)

    def resetBG(self):
        self.Buffer = None
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
        if self.bgColor:
            dc.SetBackground(wx.Brush(self.bgColor))
        else:
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        self.Drawcircle(dc)
        dc.SelectObject(wx.NullBitmap)
        return True

    def Drawcircle(self,dc):
        size=self.GetClientSize()
        pen=wx.Pen('black',4)
        dc.SetPen(pen)
        dc.SetBrush(wx.Brush(self.signalColor))
        dc.DrawCircle(size.width/2,size.height/2,50)

        # Signal Name
        dc.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        text = wx.GetApp().TopWindow.signalName
        textX,void,void,void = dc.GetFullTextExtent(text)
        dc.DrawText(text, size.width/2 - textX/2, 5)

        # Signal Address
        dc.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
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
        self.Drawcircle(dc)



from threading import Thread
from wx.lib.pubsub import Publisher

class SsignalThread(Thread):
    """
    Puts ssignal.signal into a Thread, so the GUI won't block if the
    RPC server starts its own main loop
    """
    def __init__(self, name, states, defaultState, host="localhost", port=8000):
        self.signalname = name
        self.states = states
        self.defaultState = defaultState
        self.host = host
        self.port = port

        Thread.__init__(self)
        self.setDaemon(True)
        self.start()

    def run(self):
        signal = SsignalWrapper(self.signalname, self.states, self.defaultState, self.host, self.port)


def main(name, port=8000):
    app=wx.App()

    host = socket.gethostbyname(socket.getfqdn())
    port = port

    frame=SketchFrame(parent=None, title=name, signalName=name, adressString = "{}:{}".format(host,port))
    frame.Show(True)
    frame.ToggleWindowStyle(wx.STAY_ON_TOP)

    SsignalThread(name, ("red","green"), "red", host=host, port=port)

    app.MainLoop()


if __name__=='__main__':
    main("S1")
