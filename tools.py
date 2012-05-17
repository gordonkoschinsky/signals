import sys
import os.path
import __builtin__

# Sets the homepath variable (you can change the name) to the directory where your application is located (sys.argv[0]).
__builtin__.__dict__['homepath'] = os.path.abspath(os.path.dirname(sys.argv[0]))

def getFullPath(pathList):
    """ Joins the homepath of the script with 'path' and returns the full path
    Call like getFullPath(('..','res','shape.png'))
    """
    fullpath = os.path.join(homepath, *pathList)
    return fullpath
