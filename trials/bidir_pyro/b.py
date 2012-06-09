from __future__ import print_function
import sys
import Pyro4
#Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"
import threading
import time

if sys.version_info<(3,0):
    input=raw_input


class B(object):
    def __init__(self):
        self.pingInterval = 3

        self.a = None
        self.a_pyroname = "PYRONAME:a"
        self.daemon = Pyro4.Daemon()
        self.daemon.register(self)

    def sendMessage(self,value):
        print("B: Sending Message to A: {}".format(value))
        self.a.remoteSendMessage(value)

    def remoteSendMessage(self, value):
        print("B: remoteSendMessage: {}".format(value))

    def events(self):
        self.daemon.events(self.daemon.sockets)

    def run(self):
        def ping():
            while True:
                if self.a:
                    print("B: Pinging back")
                    try:
                        self.a.remotePing()
                    except Pyro4.errors.CommunicationError:
                        self.a = None
                else:
                    # Try to reestablish connection to A
                    print("B: Trying to reestablish connection to A..")
                    try:
                        self.a = Pyro4.Proxy(self.a_pyroname)
                        self.a.remotePing()
                        self.a.addB(self)
                    except Pyro4.errors.PyroError:
                        print("Unsuccessful.")
                        self.a = None
                time.sleep(self.pingInterval)

        thread=threading.Thread(target=ping)
        thread.setDaemon(True)
        thread.start()

def main():
    b=B()
    b.run()

    while True:
        b.events()
    #daemon.requestLoop()

if __name__ == "__main__":
    main()
