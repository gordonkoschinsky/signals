import wx
from gui_signalbutton import SignalButton



class RailDiagram(wx.Panel):
    def __init__ (self, parent):
        wx.Panel.__init__(self, parent)

        self.Buffer = None
        self.SetBackgroundColour('blue')

        self.sig_s1 = SignalButton(parent=self, pos = (20,20),
                signalName="S1")


        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnPaint)
        #self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack)

    def InitBuffer(self):
        size=self.GetClientSize()
        # if buffer exists and size hasn't changed do nothing
        if self.Buffer is not None and self.Buffer.GetWidth() == size.width and self.Buffer.GetHeight() == size.height:
            return False

        self.Buffer=wx.EmptyBitmap(size.width,size.height)
        dc=wx.MemoryDC()
        dc.SelectObject(self.Buffer)
        self.DrawDiagram(dc)
        dc.SelectObject(wx.NullBitmap)
        return True

    def DrawDiagram(self,dc):
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()

        size=self.GetClientSize()

        pen=wx.Pen('black',4)
        dc.SetPen(pen)
        dc.SetBrush(wx.Brush('black'))

        #dc.DrawPolygon(((0,cs),(0,hs),(ws,hs),(ws,cs),(ws-cs,0),(cs,0)), xoffset=soffsetx, yoffset=soffsety)

        dc.SetFont(wx.Font(16, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        text = "Sometext"
        textX,void,void,void = dc.GetFullTextExtent(text)
        dc.DrawText(text, size.width/2 - textX/2, 0)


    def OnEraseBack(self, event):
        pass # do nothing to avoid flicker

    def OnPaint(self, event):
        if self.InitBuffer():
            self.Refresh() # buffer changed paint in next event, this paint event may be old
            return

        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.Buffer, 0, 0)
        self.DrawDiagram(dc)
