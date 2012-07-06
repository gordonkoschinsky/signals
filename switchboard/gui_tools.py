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
    error image if unsuccesful, and finally scaled the bitmap to scale_x, scale_y.
    """
    bmp = checkBitmapOk(wx.Bitmap(getFullPath(bitmapPath)))
    return scaleBitmap(bmp, scale_x, scale_y)
