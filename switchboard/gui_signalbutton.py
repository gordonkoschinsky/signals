import wx
from gui_shapedbutton import ShapedButton
from pubsub import pub
from gui_tools import getScaledBitmap, scaleBitmap
import error_image

class SignalButton(ShapedButton):
    def __init__(self, parent, signalName, **kwargs):
        self.width = 25
        self.height = 10

        self.Hp0Img=getScaledBitmap(('res','signal_red.png'), self.width, self.height)
        self.Ks1Img=getScaledBitmap(('res','signal_green.png'), self.width, self.height)

        self.EmptyImg=wx.wx.EmptyBitmapRGBA(self.width, self.height, 0, 0, 0, 0)

        super(SignalButton, self).__init__(parent, self.EmptyImg, pressedImg=None, disabledImg=None, **kwargs)
        # Start with an empty image unless state information is received

        self.signalName = signalName
        self.blinking = False
        self._blinkState = False
        self.state = None

        self._stateMap = {
                        None:scaleBitmap(error_image.getfatalErrorBitmap(), self.width, self.height),
                        "Hp0":self.Hp0Img,
                        "Ks1":self.Ks1Img,
                        "Ks2":None
                        }

        TIMER_ID = wx.NewId()
        self.blinkTimer = wx.Timer(self, TIMER_ID)
        self.Bind(wx.EVT_TIMER, self.onBlinkTimer, self.blinkTimer)
        self.Bind(wx.EVT_BUTTON, self.onClicked)

        # Until the first state datagream arrives, the signal state is unknown
        # and the button thus blinking
        self.startBlinking()

        pub.subscribe(self.onStateDatagram, "signal.{}.stateDatagram".format(self.signalName))

    def onStateDatagram(self, datagram):
        if datagram['signalError']:
            self.startBlinking()
        elif self.blinking:
            self.stopBlinking()
        self.state = datagram["state"]
        if not self.blinking:
            self.currentImg = self._stateMap[self.state]
            self.Refresh()

    def startBlinking(self):
        if not self.blinking:
            self.blinking = True
            self.blinkTimer.Start(500)

    def stopBlinking(self):
        self.blinking = False
        self.blinkTimer.Stop()
        self.currentImg = self._stateMap[self.state]
        self.Refresh()

    def onBlinkTimer(self, event):
        if self.blinking:
            self._blinkState = not self._blinkState
            if self._blinkState:
                self.currentImg = self.EmptyImg
            else:
                self.currentImg = self._stateMap[self.state]
            self.Refresh()

    def onClicked(self, event):
        pass
