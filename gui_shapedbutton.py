"""
A wxPython widet that takes the shape of arbitrary images.

Credits to Foglebird (Michael Fogleman), who answered this stackoverflow question
http://stackoverflow.com/questions/6449709/wxpython-changing-the-shape-of-bitmap-button
with his brilliant solution
"""
import wx

class ShapedButton(wx.PyControl):
    def __init__(self, parent, normalImg, pressedImg=None, disabledImg=None, **kwargs):
        super(ShapedButton, self).__init__(parent, -1, style=wx.BORDER_NONE |
                                                            wx.TAB_TRAVERSAL,
                                                            **kwargs)

        self.normal = normalImg
        self.pressed = pressedImg
        self.disabled = disabledImg
        self.currentImg = normalImg
        self.region = wx.RegionFromBitmapColour(normalImg, wx.Color(0, 0, 0, 0))

        # take the image size as client size, leave 3 pixel at each side for the focus border
        w, h = self.normal.GetSize()
        self.SetClientSize((w+6, h+6))

        self._clicked = False
        self._hasFocus = False



        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_dclick)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave_window)

        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_loseFocus)

    def DoGetBestSize(self):
        return self.normal.GetSize()

    def Enable(self, *args, **kwargs):
        super(ShapedButton, self).Enable(*args, **kwargs)
        self.Refresh()

    def Disable(self, *args, **kwargs):
        super(ShapedButton, self).Disable(*args, **kwargs)
        self.Refresh()

    def AcceptsFocus(self):
        return True

    def AcceptsFocusFromKeyboard(self):
        return True

    def post_event(self):
        event = wx.CommandEvent()
        event.SetEventObject(self)
        event.SetEventType(wx.EVT_BUTTON.typeId)
        wx.PostEvent(self, event)

    def on_focus(self, event):
        self._hasFocus = True

    def on_loseFocus(self, event):
        self._hasFocus = False
        self.Refresh()

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        dc.Clear()
        bitmap = self.currentImg

        if self.clicked:
            bitmap = self.pressed or bitmap
        if not self.IsEnabled():
            bitmap = self.disabled or bitmap
        dc.DrawBitmap(bitmap, 3, 3) # 3 pixel offset for focus border

        if self._hasFocus:
            w, h = self.GetClientSize()
            dc.SetBrush(wx.Brush("black", style=wx.TRANSPARENT))
            dc.SetPen(wx.Pen("white",2))
            dc.DrawRectangle(0,0,w,h)

    def set_clicked(self, clicked):
        if clicked != self._clicked:
            self._clicked = clicked
            self.SetFocus()
            self.Refresh()

    def get_clicked(self):
        return self._clicked

    clicked = property(get_clicked, set_clicked)

    def on_left_down(self, event):
        x, y = event.GetPosition()
        if self.region.Contains(x, y):
            self.clicked = True

    def on_left_dclick(self, event):
        self.on_left_down(event)

    def on_left_up(self, event):
        if self.clicked:
            x, y = event.GetPosition()
            if self.region.Contains(x, y):
                self.post_event()
        self.clicked = False

    def on_motion(self, event):
        if self.clicked:
            x, y = event.GetPosition()
            if not self.region.Contains(x, y):
                self.clicked = False

    def on_leave_window(self, event):
        self.clicked = False



def demo():
    def on_button(event):
        print 'Button was clicked.'

    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'Shaped Button Demo')
    import wx.lib.scrolledpanel as scrolled
    panel = scrolled.ScrolledPanel(frame, -1)
    panel.SetupScrolling()

    button = ShapedButton(panel,
        wx.Bitmap("C:\\Users\\gordon\\Documents\\Coding\\Signals\\res\\shape.png"),
        #wx.Bitmap('C:\Users\gordon\Documents\Coding\Signals\res\shape_p.png'),
        pos=(60,20))

    button.Bind(wx.EVT_BUTTON, on_button)

    #sizer = wx.BoxSizer(wx.VERTICAL)
    #sizer.AddStretchSpacer(1)
    #sizer.Add(button, 0, wx.ALIGN_CENTER)
    #sizer.AddStretchSpacer(1)
    #panel.SetSizer(sizer)

    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    demo()
