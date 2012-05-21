from pubsub import pub
import Pyro4
Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"

class PyroPub(object):
    """ Send messages to our signal logic server"""
    def __init__(self, server):
        self.signalServer = server

    def sendMessage(self, topic, **kwargs):
        """send the message to the remote server and also locally via pubsub
        """
        self.signalServer.sendMessage(topic, **kwargs)
        pub.sendMessage(topic, **kwargs)

_pyropub = PyroPub(Pyro4.Proxy("PYRONAME:Signals.SignalServer"))
sendMessage = _pyropub.sendMessage
