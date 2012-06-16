"""
A custom wx.StatusBar class that can handle colored backgrounds for each of its fields

Major parts taken from the wxpython demo code.
"""

import wx
from pubsub import pub

class SwitchboardStatusBar(wx.StatusBar):
    def __init__(self, parent, fieldCount=1, fieldColors=()):
        """
        A custom statusbar with StaticText controls as fields.
        The StaticText can be colored as desired.
        The number of fields can not change at runtime.
        fieldCount: int
        fieldColors: Iterable wx-valid color values for each field
        """
        wx.StatusBar.__init__(self, parent, wx.ID_ANY)

        self.fieldCountSet = False
        self.SetFieldsCount(fieldCount)

        self.staticTexts = []

        self.staticTexts = [
                wx.StaticText(parent=self)
                for i in range(fieldCount)]

        self.fieldColors = fieldColors

        colorLen = len(fieldColors)
        if colorLen < fieldCount:
            self.fieldColors = ["nocolor" for i in range(fieldCount)]
            for i,color in enumerate(fieldColors):
                self.fieldColors[i] = color

        self.sizeChanged = False

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        pub.subscribe(self.OnConnectionError, "InterlockingCom.connection.error")
        pub.subscribe(self.OnConnectionEstablished, "InterlockingCom.connection.established")

        # set the initial position of the fields
        self.Reposition()

    def OnSize(self, evt):
        self.Reposition()  # for normal size events

        # Set a flag so the idle time handler will also do the repositioning.
        # It is done this way to get around a buglet where GetFieldRect is not
        # accurate during the EVT_SIZE resulting from a frame maximize.
        self.sizeChanged = True

    def OnIdle(self, evt):
        if self.sizeChanged:
            self.Reposition()

    def OnConnectionError(self):
        self.SetStatusBackground("red", 0)
        self.SetStatusText("Interlocking connection faulty", 0)

    def OnConnectionEstablished(self):
        self.SetStatusBackground("green", 0)
        self.SetStatusText("Interlocking connection OK", 0)

    def SetFieldsCount(self, number):
        """
        Set the number of fields, but only once!
        This is called by the constructor, and thus not callable when the object
        has been instantiated.
        """
        if self.fieldCountSet:
            raise NotImplementedError
        else:
            wx.StatusBar.SetFieldsCount(self, number)
            self.fieldCountSet = True

    def SetStatusBackground(self, fieldColor, fieldNumber):
        self.fieldColors[fieldNumber] = fieldColor
        self.sizeChanged = True

    def SetStatusText(self, text, fieldNumber):
        self.staticTexts[fieldNumber].SetLabel(text)

    def Reposition(self):
        for fieldnum in range(self.GetFieldsCount()):
            rect = self.GetFieldRect(fieldnum)
            self.staticTexts[fieldnum].SetPosition((rect.x+2, rect.y+2))
            self.staticTexts[fieldnum].SetSize((rect.width-4, rect.height-4))
            self.staticTexts[fieldnum].SetBackgroundColour(self.fieldColors[fieldnum])

        self.sizeChanged = False
