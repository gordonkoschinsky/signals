"""
some tools to help with the GUI
"""

import sys
import os.path
import __builtin__
import wx

# Sets the homepath variable (you can change the name) to the directory where your application is located (sys.argv[0]).
__builtin__.__dict__['homepath'] = os.path.abspath(os.path.dirname(sys.argv[0]))

def getFullPath(pathList):
    """ Joins the homepath of the script with 'path' and returns the full path
    Call like getFullPath(('..','res','shape.png'))
    """
    fullpath = os.path.join(homepath, *pathList)
    return fullpath

def checkBitmapOk(bmp):
    """
    If the isOk() method of the bitmap 'bmp' returns false,
    change bmp to be  the "fatal error" bitmap
    returns the original bmp or the error bmp
    """
    if not bmp.IsOk():
        import error_image
        bmp = error_image.getfatalErrorBitmap()
    return bmp

def scaleBitmap(bmp, scale_x, scale_y):
    """
    Scales the bitmap to scale_x, scale_y dimensions
    returns the scaled bitmap
    """
    img = wx.ImageFromBitmap(bmp)
    img.Rescale(scale_x, scale_y, wx.IMAGE_QUALITY_HIGH)
    bmp = wx.BitmapFromImage(img)
    return bmp

def getScaledBitmap(bitmapPath, scale_x, scale_y):
    """Extends the homepath of the application with the tuple bitmapPath,
    tries to load the file at this path into a wx.Bitmap, makes the bitmap an
    error image if unsuccesful, and finally returns the scaled
    bitmap (scaled to scale_x, scale_y).
    """
    bmp = checkBitmapOk(wx.Bitmap(getFullPath(bitmapPath)))
    return scaleBitmap(bmp, scale_x, scale_y)



###################### SKIN UI ####################################

class SkinPanel(wx.Panel):
    """
    A panel with the ability to extract part of its background.
    That way, child widgets can use the background to draw themselves "transparently",
    which, of course, is a fake transparency, but should work well

    The panel can use a bitmap to draw its background.
    The bitmap can be tiled over all the space occupied by the panel by using the
    SkinPanel.TILED in the 'style' parameter of the SetBitmap function.

    Found at http://www.gooli.org/blog/snippets/
    by Eli Golovinsky
    modified to use auto double buffering by Gordon Koschinsky
    """

    # Styles
    NORMAL = 0
    TILED = 1
    STRETCHED = 2

    def __init__(self, parent=None):
        self._bitmap =  None
        self._style = self.NORMAL
        self._Buffer = None # A canvas for double buffering,

        # Prepare for use both in XRC and in-code creation
        if parent:
            wx.Panel.__init__(self, parent)
        else:
            pre = wx.PrePanel()
            self.PostCreate(pre)

        self.Bind(wx.EVT_PAINT, self.__on_paint)
        self.Bind(wx.EVT_SIZE, self.__on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.__on_erase_background)

        self.__on_size(None)

    def SetBitmap(self, bitmap, style=NORMAL, resetSize=True):
        """Sets the bitmap that will be displayed in the panel's background"""
        self._bitmap = bitmap
        self._style = style
        self._Buffer = None
        if resetSize:
            self.SetMinSize(bitmap.GetSize())
            if self.GetContainingSizer():
                self.GetContainingSizer().Layout()
        self.Refresh()

    def GetBackgroundRect(self, rect):
        """
        Returns a portion of the panel's background.
        Widgets in this module use this ability to be painted transparently.
        """
        res = wx.EmptyBitmap(rect.width, rect.height)
        resdc = wx.MemoryDC()
        resdc.SelectObject(res)
        resdc.SetBackground(wx.Brush(self.GetBackgroundColour()))

        if self._Buffer:
            canvasdc = wx.MemoryDC()
            canvasdc.SelectObject(self._Buffer)
            resdc.Blit(0, 0, rect.width, rect.height, canvasdc, rect.x, rect.y)
            resdc.SelectObject(wx.NullBitmap)

        return res

    def __on_size(self, evt):
        # The Buffer init is done here, to make sure the buffer is always
        # the same size as the Window
        size  = self.GetSize()

        # Make new offscreen bitmap: this bitmap will always have the
        # current drawing in it, so it can be used to save the image to
        # a file, or whatever.
        self._Buffer = wx.EmptyBitmap(*size)
        self.UpdateDrawing()

    def __on_paint(self, evt):
        dc = wx.BufferedPaintDC(self, self._Buffer)

    def UpdateDrawing(self):
        dc = wx.MemoryDC()
        dc.SelectObject(self._Buffer)
        self.Draw(dc)
        del dc # need to get rid of the MemoryDC before Update() is called.
        self.Refresh(eraseBackground=False)
        self.Update()

    def Draw(self, dc):
        (w, h) = self.GetSize()

        # Use double buffering instead of background erasing to prevent flicker.
        # Redraw the panel from the background bitmap only if the canvas is empty,
        # which happens when the panel is resised or the background bitmap is
        # changed.

        # If this panel has a bitmap background, use it
        if self._bitmap is not None:
            (bw, bh) = self._bitmap.GetSize()
            #self._Buffer = wx.EmptyBitmap(max(w, bw), max(h, bh))
            dc.SelectObject(self._Buffer)
            dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
            dc.Clear()
            self._draw_background(dc)

        # Otherwise use the parent panel background
        else:
            #self._Buffer = wx.EmptyBitmap(w, h)
            dc.SelectObject(self._Buffer)

            # Get the panel background if it supports it (SkinPanel does),
            # otherwise just use the parent's background color
            if hasattr(self.GetParent(), "GetBackgroundRect") and self.GetRect():
                backgroundBitmap = self.GetParent().GetBackgroundRect(self.GetRect())
                dc.DrawBitmap(backgroundBitmap, 0, 0, False)
            else:
                dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
                dc.Clear()


    def __on_erase_background(self, event):
        event.Skip(False)

    def _draw_background(self, dc):
        if self._bitmap is not None and self._bitmap is not wx.NullBitmap:
            (w, h) = self.GetSize()
            (bw, bh) = self._bitmap.GetSize()
            if self._style == self.TILED:
                # If the bitmap should be tiled, draw it enough times to fill the panel.
                x = 0
                while x < w+bw:
                    y = 0
                    while y < h+bh:
                        dc.DrawBitmap(self._bitmap, x, y, False)
                        y += bh
                    x += bw
            elif self._style == self.STRETCHED:
                # If the bitmap should be stretched, convert it to wx.Image and
                # scale it
                image = self._bitmap.ConvertToImage()
                image.Rescale(w, h)
                dc.DrawBitmap(image.ConvertToBitmap(), 0, 0, False)
            else:
                # Otherwise, center the bitmap in the panel
                (x, y) = ((w-bw)/2, (h-bh)/2)
                #x, y = 0, 0
                dc.DrawBitmap(self._bitmap, x, y, False)
                return (x, y, bw, bh)

# ------------------------------------------------------------------------------

class SkinButton(wx.PyControl):
    class SkinButtonEvent(wx.PyCommandEvent):
        """Event sent by skin buttons when they are clicked"""
        def __init__(self, eventType, ID):
            wx.PyCommandEvent.__init__(self, eventType, ID)

    def __init__(self, parent, ID, defaultBitmap, selectedBitmap,
                  hotBitmap, disabledBitmap, label):
        wx.PyControl.__init__(self, parent, ID,
                          wx.DefaultPosition,
                          wx.DefaultSize,
                          wx.BORDER_NONE)

        # Init
        self.SetLabel(label)
        self._defaultBitmap = defaultBitmap
        self._selectedBitmap = selectedBitmap
        self._hotBitmap = hotBitmap
        self._disabledBitmap = disabledBitmap
        self._up = True
        self._mouseInside = False
        self._labelColor = None
        self._labelShadowColor = None
        self.SetSize(self._defaultBitmap.GetSize())
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

        # Bind events
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION,  self.on_motion)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.__on_erase_background)
        self.Bind(wx.EVT_PAINT,  self.__on_paint)

    def DoGetBestSize(self):
        """
        Overridden base class virtual.
        The best size of the button is based on the bitmap size.
        """
        return self._defaultBitmap.GetSize()

    def AcceptsFocus(self):
        """
        Overridden base class virtual.
        A skinned button only works with a mouse.
        """
        return False

    def Enable(self, enable=True):
        wx.PyControl.Enable(self, enable)
        self.Refresh()

    def Disable(self):
        wx.PyControl.Enable(self, False)
        self.Refresh()

    def SetLabelColors(self, color, shadowColor):
        self._labelColor = color
        self._labelShadowColor = shadowColor

    def _notify(self):
        event = self.SkinButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)

    def _get_background_color(self):
        return self.GetParent().GetBackgroundColour()

    def _calc_label_position(self, bitmapSize, textSize):
        (tw, th) = textSize
        (bw, bh) = bitmapSize
        x = (bw-tw)/2
        y = bh-th
        return (x, y)

    def on_left_down(self, event):
        if not self.IsEnabled():
            return
        self._up = False
        self.CaptureMouse()
        self.SetFocus()
        self.Refresh()
        event.Skip()

    def on_left_up(self, event):
        if not self.IsEnabled() or not self.HasCapture():
            return
        if self.HasCapture():
            self.ReleaseMouse()
            if not self._up:    # if the button was down when the mouse was released...
                self._notify()
            self._up = True
            self.Refresh()
            event.Skip()

    def on_motion(self, event):
        """
        If the mouse moved outside the button while the left button was
        down, the click is cancelled.
        """
        if not self.IsEnabled() or not self.HasCapture():
            return
        if event.LeftIsDown() and self.HasCapture():
            x,y = event.GetPositionTuple()
            w,h = self.GetClientSizeTuple()
            if self._up and x<w and x>=0 and y<h and y>=0:
                self._up = False
                self.Refresh()
                return
            if not self._up and (x<0 or y<0 or x>=w or y>=h):
                self._up = True
                self.Refresh()
                return
        event.Skip()

    def on_enter(self, event):
        self._mouseInside = True
        self.Refresh()
        event.Skip()

    def on_leave(self, event):
        self._mouseInside = False
        self.Refresh()
        event.Skip()

    def on_key_down(self, event):
        self.GetParent().AddPendingEvent(event)

    def on_key_up(self, event):
        self.GetParent().AddPendingEvent(event)

    def __on_erase_background(self, event):
        event.Skip(False)

    def __on_paint(self, event):
        dc = wx.PaintDC(self)
        (w, h) = self.GetSize()

        # Use double buffering instead of background erasing to prevent flicker.
        mdc = wx.MemoryDC()
        temp = wx.EmptyBitmap(w, h)
        mdc.SelectObject(temp)

        # Get the panel background if it supports it (SkinPanel does),
        # otherwise just use the parent's background color
        if hasattr(self.GetParent(), "GetBackgroundRect") and self.GetRect():
            backgroundBitmap = self.GetParent().GetBackgroundRect(self.GetRect())
            mdc.DrawBitmap(backgroundBitmap, 0, 0, False)
        else:
            brush = wx.Brush(self._get_background_color())
            mdc.SetBackground(brush)
            mdc.Clear()

        # Draw a bitmap according to the current state
        if not self.IsEnabled():
            bitmap = self._disabledBitmap
        elif not self._up:
            bitmap = self._selectedBitmap
        elif self._mouseInside:
            bitmap = self._hotBitmap
        else:
            bitmap = self._defaultBitmap
        mdc.DrawBitmap(bitmap, 0, 0, False)

        # Draw the label
        mdc.SetFont(self.GetFont())
        textSize = mdc.GetTextExtent(self.GetLabel())
        (x,  y) = self._calc_label_position(self._defaultBitmap.GetSize(), textSize)

        if self.IsEnabled():
            if self._labelShadowColor:
                mdc.SetTextForeground(self._labelShadowColor)
                mdc.DrawText(self.GetLabel(), x+1, y+1)

            mdc.SetTextForeground(self._labelColor)
            mdc.DrawText(self.GetLabel(), x, y)
        else:
            mdc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
            mdc.DrawText(self.GetLabel(), x, y)

        # Copy the temp bitmap to the screen
        dc.Blit(0, 0, w, h, mdc, 0, 0)
        mdc.SelectObject(wx.NullBitmap)
