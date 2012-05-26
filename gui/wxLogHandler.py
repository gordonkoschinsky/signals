import logging
import wx

class WxLogHandler(logging.Handler):
    """A simple logging.Handler that takes a reference to a wx.TextCtrl and
    appends the formated log records to that widget.
    Credits to Peter Damoc
    """
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        wx.CallAfter(self.ctrl.AppendText, self.format(record)+"\n")
