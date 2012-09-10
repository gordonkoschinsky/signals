"""
A wxPython widet that takes the shape of arbitrary images.

Credits to Foglebird (Michael Fogleman), who answered this stackoverflow question
http://stackoverflow.com/questions/6449709/wxpython-changing-the-shape-of-bitmap-button
with his brilliant solution
"""
import wx

class ShapedButton(wx.PyControl):
    def __init__(self, parent, normalImg, pressedImg=None, disabledImg=None, **kwargs):
        super(ShapedButton, self).__init__(parent, wx.ID_ANY, style=wx.BORDER_NONE |
                                                            wx.WANTS_CHARS,
                                                            **kwargs)

        self.normal = normalImg
        self.pressed = pressedImg
        self.disabled = disabledImg
        self.currentImg = normalImg
        self.region = self.GetClickRegion(normalImg)

        # take the image size as client size, leave 3 pixel at each side for the focus border
        w, h = self.normal.GetSize()
        self.borderThickness = 3
        self.SetClientSize((w+self.borderThickness*2, h+self.borderThickness*2))

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
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)

        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self.on_loseFocus)



    def GetClickRegion(self, bitmap):
        """ build the clickable region, use mask if available, else black as transparent color
        """
        if bitmap.GetMask():
            region = wx.RegionFromBitmap(bitmap)
        else:
            region = wx.RegionFromBitmapColour(bitmap, wx.Color(0, 0, 0, 0))
        return region

    def DoGetBestSize(self):
        return self.normal.GetSize()

    def GetDefaultAttributes(self):
        return wx.Button.GetClassDefaultAttributes()

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
        self.Refresh()

    def on_loseFocus(self, event):
        self._hasFocus = False
        self.Refresh()

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)

        # Get the panel background if it supports it (SkinPanel does),
        # otherwise just use the parent's background color
        if hasattr(self.GetParent(), "GetBackgroundRect") and self.GetRect():
            backgroundBitmap = self.GetParent().GetBackgroundRect(self.GetRect())
            dc.DrawBitmap(backgroundBitmap, 0, 0, False)
        else:
            brush = wx.Brush(self.GetParent().GetBackgroundColour())
            dc.SetBackground(brush)
            dc.Clear()


        #dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        #dc.Clear()
        bitmap = self.currentImg

        if self.clicked:
            bitmap = self.pressed or bitmap
        if not self.IsEnabled():
            bitmap = self.disabled or bitmap
        dc.DrawBitmap(bitmap, self.borderThickness, self.borderThickness, useMask=True)

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
        if self.region.Contains(x-self.borderThickness, y-self.borderThickness):
            self.clicked = True

    def on_left_dclick(self, event):
        self.on_left_down(event)

    def on_left_up(self, event):
        if self.clicked:
            x, y = event.GetPosition()
            if self.region.Contains(x-self.borderThickness, y-self.borderThickness):
                self.post_event()
        self.clicked = False

    def on_motion(self, event):
        if self.clicked:
            x, y = event.GetPosition()
            if not self.region.Contains(x-self.borderThickness, y-self.borderThickness):
                self.clicked = False

    def on_leave_window(self, event):
        self.clicked = False

    def on_key_down(self, event):
        key = event.GetKeyCode()

        # TODO: Add support for arrow key nagivatio
        if key == wx.WXK_TAB:
            flags = 0
            if not event.ShiftDown(): flags |= wx.NavigationKeyEvent.IsForward
            if event.CmdDown():       flags |= wx.NavigationKeyEvent.WinChange
            self.Navigate(flags)
        elif key == wx.WXK_SPACE:
            self.clicked = True
        else:
            event.Skip()

    def on_key_up(self, event):
        key = event.GetKeyCode()

        if key == wx.WXK_SPACE:
            self.clicked = False
            self.post_event()
        else:
            event.Skip()


# -------------------------------------------------------------------------------
def demo():
    import gui_tools
    def on_button(event):
        print 'Button was clicked.'

    app = wx.PySimpleApp()
    frame = wx.Frame(None, -1, 'Shaped Button Demo')
    panel = gui_tools.SkinPanel(frame)
    panel.SetBitmap(wx.Bitmap("C:/Users/gordon/Pictures/Kanada/P1010275.JPG_cellsize.png"), style = gui_tools.SkinPanel.STRETCHED)

    normalBMP = wx.Bitmap('C:/Users/gordon/Documents/Coding/Signals/src/switchboard/res/shape.png')
    pressedBMP = wx.Bitmap('C:/Users/gordon/Documents/Coding/Signals/src/switchboard/res/shape_p.png')

    button = ShapedButton(panel,
        normalBMP,
        pressedBMP,
        pos=(60,20))

    button2 = ShapedButton(panel,
        normalBMP,
        pressedBMP,
        pos=(160,30))

    wx.Button(panel, pos=(0,0))
    wx.Button(panel, pos=(0,30))

    button.Bind(wx.EVT_BUTTON, on_button)

    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    demo()
