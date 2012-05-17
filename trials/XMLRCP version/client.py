import rpctools
import xmlrpclib
from time import sleep
import socket


s1 = rpctools.getRPCtimeoutProxy(host="zampano")

try:

    print s1.getState()
    try:
        print s1.changeStateTo("green")
    except socket.timeout:
        print "Timed out."

    try:
        print s1.getState()
    except socket.timeout:
        print "Timed out."


    print s1.getState()
    #sleep(1)
    print s1.getState()
    #sleep(0.5)
    print s1.getState()
    #sleep(1)
    print s1.getState()

    try:
        print s1.changeStateTo("red")
    except socket.timeout:
        print "Timed out."

    # Print list of available methods
    print s1.system.listMethods()
except xmlrpclib.ProtocolError:
    print("Could not connect to server.")
