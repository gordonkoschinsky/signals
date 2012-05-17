from threading import Thread, Event
from Pyro4 import naming

class NameServer(Thread):
    def __init__(self, hostname):
        super(NameServer,self).__init__()
        self.setDaemon(1)
        self.hostname=hostname
        self.started=Event()

    def run(self):
        # start the nameserver, it configures a broadcast server for us
        self.uri, self.ns_daemon, self.bc_server = naming.startNS(self.hostname)
        # start this broadcast server in its own thread
        self.bc_server.runInThread()
        # signal the main thread that setup is sone
        self.started.set()
        # serve away...
        self.ns_daemon.requestLoop()


def startNameServer(host):
    ns=NameServer(host)
    ns.start()
    ns.started.wait()
    return ns
