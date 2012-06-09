"""
Module for communication with the interlocking system

Connects to the interlocking server via Pyro4 a
and registers its own Pyro4 server for callbacks from the interlocking

Provides a pubsub-like remote sendmessage() method.
"""
import logging
import time
import threading

import uuid
switchboardUUID = uuid.uuid1()

from pubsub import pub
from threadsafepub import pub as tpub

import Pyro4
Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"

class InterlockingCom(object):
    """ Communicate with the signal logic server"""
    def __init__(self, switchboardUUID):
        self.pingInterval = 3

        self.logger = logging.getLogger('interlockingCom')

        self.interlocking = None
        self.interlocking_pyroname = "PYRONAME:signals.interlockingServer"
        self.daemon = Pyro4.Daemon()
        self.daemon.register(self)


    def sendMessage(self, topic, **kwargs):
        """send the message to the remote server and also locally via pubsub
        """
        self.logger.debug("Sending message to interlocking server: {}".format(topic))
        self.interlocking.sendMessage(topic, **kwargs)
        pub.sendMessage(topic, **kwargs)

    def callback(self, topic, **kwargs):
        tpub.sendMessage(topic, **kwargs)

    def run(self):
        def ping():
            while True:
                if self.interlocking:
                    self.logger.debug("Pinging back interlocking server")
                    try:
                        self.interlocking.remotePing()
                    except Pyro4.errors.CommunicationError:
                        self.interlocking = None
                else:
                    # Try to reestablish connection to A
                    self.logger.debug("Trying to reestablish connection to interlocking server...")
                    try:
                        self.interlocking = Pyro4.Proxy(self.interlocking_pyroname)
                        self.interlocking.remotePing()
                        self.interlocking.registerSwitchboard(self)
                    except Pyro4.errors.PyroError:
                        self.logger.debug("Unsuccessfully tried to reestablish connection to interlocking server.")
                        self.interlocking = None
                time.sleep(self.pingInterval)

        def eventLoop():
            self.daemon.requestLoop()


        pingThread=threading.Thread(target=ping)
        pingThread.setDaemon(True)
        pingThread.start()

        eventThread = threading.Thread(target=eventLoop)
        eventThread.setDaemon(True)
        eventThread.start()



_interlockingCom = InterlockingCom(switchboardUUID)
sendMessage = _interlockingCom.sendMessage

_interlockingCom.run()


