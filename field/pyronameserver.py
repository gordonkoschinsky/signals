from threading import Thread, Event
from Pyro4 import naming
import Pyro4

Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"

class NameServer(Thread):
    def __init__(self, hostname=None):
        super(NameServer,self).__init__()
        self.setDaemon(1)
        self.hostname=hostname
        self.started=Event()

    def run(self):
        # start the nameserver, it configures a broadcast server for us
        self.uri, self.ns_daemon, self.bc_server = naming.startNS(host=self.hostname)
        # start this broadcast server in its own thread
        self.bc_server.runInThread()
        # signal the main thread that setup is done
        self.started.set()
        # serve away...
        self.ns_daemon.requestLoop()


def startNameServer(host):
    ns=NameServer(host)
    ns.start()
    ns.started.wait()
    return ns


if __name__ == "__main__":
    # Stand-alone nameserver
    import sys

    ns = startNameServer(Pyro4.socketutil.getMyIpAddress(workaround127=True))
    print "Nameserver started at {}".format(ns.uri)
    print "Broadcastserver started at {}".format(ns.bc_server.locationStr)
    sys.stdout.flush()

    ns.join()
