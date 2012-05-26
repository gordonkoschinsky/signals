"""
Setup the "logical" signals, i.e. the interlocking logic represented by
individual Csignal instances.
Starts up a Pyro4 server for interactions with the GUI process

    TODO: GUI SEPERATION:
    - Make main.py just setup all signals, no GUI
    - make main start a seperate thread with its own pyro server to take commands
    from the GUI process. The GUI process also polls status and error information
    via Pyro from main

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


signals = signalregistry.Registry()


s1 = csignal.Signal("S1", signals)
s1.configure()
s1.addRequirement("Ks1", "S2", "Hp0")
s1.configCompleted()

s2 = csignal.Signal("S2", signals)
s2.configure()
s2.configCompleted()

logger.debug("Signal setup completed")

class SignalServer(object):
    def __init__(self):
        ns = Pyro4.locateNS()
        self.daemon = Pyro4.Daemon()
        uri = self.daemon.register(self)
        ns.register("Signals.SignalServer", uri)

    def start(self):
        self.daemon.requestLoop()

    def sendMessage(self, topic, **kwargs):
        logger.debug("Received message to send: {} {}".format(topic, kwargs))
        pub.sendMessage(topic, **kwargs)

logger.debug("Starting signal server...")

SignalServer().start()

