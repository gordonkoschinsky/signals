from __future__ import print_function
import Pyro4
#Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"

import time
import threading

class A(object):
    def __init__(self):
        self.bs=[]

        self.ns=Pyro4.locateNS()
        self.daemon = Pyro4.Daemon()
        a_uri=self.daemon.register(self)
        self.ns.register("a", a_uri)



    def addB(self, b):
        self.bs.append(b)

    def sendMessage(self, value):
        print(self.ns.list(prefix="b"))
        for b in self.bs:
            print("A: Sending message to B ({})".format(b))
            try:
                b.remoteSendMessage(value)
            except Pyro4.errors.CommunicationError:
                self.bs.remove(b)

    def remoteSendMessage(self, value):
        print("A: remoteSendMessage: {}".format(value))

    def remotePing(self):
        """
        called by a remote b to ping us back
        Does nothing, if the connection is sane, the call will suceed
        """
        print("A: Got pinged by a B")
        pass

    def run(self):
        def ping():
            while True:
                time.sleep(3)
                print("A: Pinging back")
                self.sendMessage("test value")

        thread=threading.Thread(target=ping)
        thread.setDaemon(True)
        thread.start()
        print("A running.")
        self.daemon.requestLoop()

def main():


    a=A()
    a.run()




if __name__ == "__main__":
    main()
