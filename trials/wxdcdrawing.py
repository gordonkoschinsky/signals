"""
A simple wx wrapper around a ssginal.py RPC signal server.
Flashes its background if the state is polled,
and shows red/green state as a circle
"""

import wx
import sys

class SketchFrame(wx.Frame):
    def __init__(self, parent):

        wx.Frame.__init__(self, parent, -1, "Sketch Frame",size=(140,350))

        # WIDGETS
        self.panel = wx.Panel(self)
        self.sketch = SketchWindow(self.panel, wx.ID_ANY)
        testButton = wx.Button(self.panel, label="Test Signal Flash")

        # SIZERS
        topSizer = wx.BoxSizer(wx.VERTICAL)

        sketchSizer = wx.BoxSizer(wx.HORIZONTAL)
        sketchSizer.Add(self.sketch, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)

        topSizer.Add(testButton, flag=wx.ALL|wx.EXPAND, border=5)
        topSizer.Add(sketchSizer, proportion=1,flag=wx.ALL|wx.EXPAND)
        self.panel.SetSizer(topSizer)

        testButton.Bind(wx.EVT_BUTTON, self.onTestFlash)

    def onTestFlash(self, event):
        self.sketch.flashBG(event)


class SketchWindow(wx.Window):
    def __init__ (self, parent,ID):
        wx.Window.__init__(self, parent, ID)

        self.Buffer = None
        self.bgColor = wx.NullColor

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack)


    def flashBG(self, event):
        print "timer"
        sys.stdout.flush()
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
        pen=wx.Pen('blue',4)
        dc.SetPen(pen)
        dc.DrawCircle(size.width/2,size.height/2,50)

    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh() # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.Drawcircle(dc)

if __name__=='__main__':
    app=wx.PySimpleApp()
    frame=SketchFrame(None)
    frame.Show(True)
    app.MainLoop()
