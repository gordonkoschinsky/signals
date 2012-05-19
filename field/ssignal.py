"""Simple signal server
Acts as "the actual real world signal". As such, it contains no logic, but
just holds state and can change its state upon request.

Listens to requests from the controller via RPyC

If this signal were real and not just a representation of a real signal,
the class would have to deal with the actual hardware to make sure the hardware
is in the right state and no hardware problems occur. This is of course left
out here. However, it should be possible to subclass this class and make a
"FaultySignal" class, that randomly changes state without being asked to etc.
Thus, we can test the fault handling in the controller.

TODO: Add a watchdog thread (Timer?). If the signal is not polled every few
seconds, fallback to save state.
"""

import rpyc
from rpyc.utils.server import ThreadedServer

from time import sleep

from pubsub import pub
import logging




class Signal(rpyc.Service):

    ALIASES = [] # needed by RPyC

    def __init__(self, conn, name, states, defaultState, host="localhost", *args, **kwargs):
        rpyc.Service.__init__(self, conn, *args, **kwargs)

        self.name = name
        self.ALIASES =[name,]
        self.host = host

        self.states = states

        if defaultState not in states:
            raise ValueError, "defaultState {} is not in the list of allowed states {}".format(defaultState, states)
        self.defaultState = defaultState
        self.currentState = self.defaultState

        self.daemonActive = True

        #nameserver.register("signal.{}".format(self.name), uri)

        #pub.sendMessage("Signal.{}.daemon".format(self.name), daemon=daemon)

        # Run the server
        #daemon.requestLoop(self.serverActive)
        self.server = ThreadedServer(self, port = 18861, autoregister = True)
        self.server.start()



    def exposed_serverActive(self):
        return self.daemonActive

    def exposed_disconnect(self):
        self.daemonActive = False

    def exposed_getState(self):
        return(self.currentState)

    def exposed_changeStateTo(self, newState):
        if newState not in self.states:
           raise ValueError, "newState {} is not in the list of allowed states {}".format(newState, self.states)

        sleep(0.5) # simulate the time it takes the hardware to change the state

        self.currentState = newState

        return self.getState()
