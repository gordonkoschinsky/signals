"""
Setup the "logical" signals, i.e. the interlocking logic represented by
individual Csignal instances.
Starts up a Pyro4 server for interactions with the GUI process

    TODO: GUI SEPERATION:
     - Register the Gui with the intelrocking server

    TODO:
    - Track diagram in the gui:
    - Parser to send commands to the elements
    - More elements: Switches, track occupancy indicators

"""

import csignal
from pubsub import pub
import signalregistry
import logging
import Pyro4
Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"

logging.basicConfig(level=logging.DEBUG)

logging.getLogger("").setLevel(logging.INFO)

logger = logging.getLogger("signals.main")
logger.setLevel(logging.DEBUG)

logging.getLogger("signals.interlockingServer").setLevel(logging.INFO)

signals = signalregistry.Registry()


s1 = csignal.Signal("S1", signals)
s1.configure()
s1.addRequirement("Ks1", "S2", "Hp0")
s1.configCompleted()

s2 = csignal.Signal("S2", signals)
s2.configure()
s2.configCompleted()

logger.debug("Signal setup completed")

class InterlockingServer(object):
    def __init__(self):
        self.switchboards = []

        ns = Pyro4.locateNS()
        self.daemon = Pyro4.Daemon()
        uri = self.daemon.register(self)
        ns.register("signals.interlockingServer", uri)

        self.logger = logging.getLogger("signals.interlockingServer")

        pub.subscribe(self.forwardMessage, pub.ALL_TOPICS)

    def start(self):
        self.logger.info("Starting interlocking server...")
        self.daemon.requestLoop()

    def remotePing(self):
        """
        called by a remote switchboard to ping back the interlocking server
        Does nothing, if the connection is sane, the call will suceed
        """
        self.logger.debug("Got pinged by a switchboard")
        pass

    def registerSwitchboard(self, switchboard):
        """
        register a switchboard callback with the interlocking server.
        Local pubsub messages are forwarded to this switchboard
        """
        self.logger.debug("Switchboard {} registered with interlocking".format(switchboard))
        self.switchboards.append(switchboard)

    def forwardMessage(self, topic=pub.AUTO_TOPIC, **kwargs):
        """
        forward a pubsub message to all registerd remote sides (switchboards)
        """
        for switchboard in self.switchboards:
            try:
                self.logger.debug("forwarding pubsub topic {} to switchboard {}".format(topic.getName(),switchboard))
                switchboard.callback(topic.getName(), **kwargs)
            except Pyro4.errors.CommunicationError:
                self.switchboards.remove(switchboard)


    def sendMessage(self, topic, **kwargs):
        """
        echo a message locally via pubsub.pub.sendMessage
        called by the remote side
        """
        self.logger.debug("Received message to send: {} {}".format(topic, kwargs))
        pub.unsubscribe(self.forwardMessage, topic)
        pub.sendMessage(topic, **kwargs)
        pub.subscribe(self.forwardMessage, pub.ALL_TOPICS)


InterlockingServer().start()
