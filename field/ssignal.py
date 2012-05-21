"""Simple signal server
Acts as "the actual real world signal". As such, it contains no logic, but
just holds state and can change its state upon request.

Listens to requests from the controller via Pyro4

If this signal was real and not just a representation of a real signal,
the class would have to deal with the actual hardware to make sure the hardware
is in the right state and no hardware problems occur. This is of course left
out here. However, it should be possible to subclass this class and make a
"FaultySignal" class, that randomly changes state without being asked to etc.
Thus, we can test the fault handling in the controller.

TODO: Add a watchdog thread (Timer?). If the signal is not polled every few
seconds, fallback to save state.
"""

import Pyro4
from time import sleep

from pubsub import pub

Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"
#Pyro4.config.SERVERTYPE = "multiplex"


class Signal(object):
    def __init__(self, name, states, defaultState, host="localhost"):
        self.name = name
        self.host = host

        self.states = states

        if defaultState not in states:
            raise ValueError, "defaultState {} is not in the list of allowed states {}".format(defaultState, states)
        self.defaultState = defaultState
        self.currentState = self.defaultState

        self.daemonActive = True

        # Create Pyro Daemon
        daemon=Pyro4.Daemon(host=host)
        nameserver=Pyro4.locateNS()
        uri=daemon.register(self)
        nameserver.register("signal.{}".format(self.name), uri)

        pub.sendMessage("Signal.{}.daemon".format(self.name), daemon=daemon)
        print "Signal {} set up.".format(self.name)
        # Run the server
        daemon.requestLoop(self.serverActive)

    def serverActive(self):
        return self.daemonActive

    def disconnect(self):
        self.daemonActive = False

    def getState(self):
        return(self.currentState)

    def changeStateTo(self, newState):
        if newState not in self.states:
           raise ValueError, "newState {} is not in the list of allowed states {}".format(newState, self.states)

        sleep(0.5) # simulate the time it takes the hardware to change the state

        self.currentState = newState

        return self.getState()
