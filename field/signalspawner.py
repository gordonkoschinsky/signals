"""
Spawns multiple processes. Each process runs a signal representation (a "field" signal), implemented
in ssignal.py and GUIed by wxsignal.py
Also starts the pyro4 nameserver
"""

from multiprocessing import Process
import wxssignal
import sys
import Pyro4
import pyronameserver as pns



if __name__ == '__main__':

    ns = pns.startNameServer(Pyro4.socketutil.getMyIpAddress(workaround127=True))
    print "Nameserver started at {}".format(ns.uri)
    print "Broadcastserver started at {}".format(ns.bc_server.locationStr)
    sys.stdout.flush()


    host = Pyro4.socketutil.getMyIpAddress(workaround127=True)

    p1 = Process(target=wxssignal.createSignalRepresentation, kwargs={"name":"S1", "host":host, "FrameX":0})
    p1.start()

    p2 = Process(target=wxssignal.createSignalRepresentation, kwargs={"name":"S2", "host":host, "FrameX":160})
    p2.start()
