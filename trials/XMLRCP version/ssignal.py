"""Simple signal server
Acts as "the actual real world signal". As such, it contains no logic, but
just holds state and can change its state upon request.

Listens to requests from the controller via XML-RPC

If this signal were real and not just a representation of a real signal,
the class would have to deal with the actual hardware to make sure the hardware
is in the right state and no hardware problems occur. This is of course left
out here. However, it should be possible to subclass this class and make a
"FaultySignal" class, that randomly changes state without being asked to etc.
Thus, we can test the fault handling in the controller.
"""

from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from time import sleep


class Signal(object):
    def __init__(self, name, states, defaultState, host="localhost", port=8000):
        self.name = name
        self.host = host
        self.port = port

        self.states = states

        if defaultState not in states:
            raise ValueError, "defaultState {} is not in the list of allowed states {}".format(defaultState, states)
        self.defaultState = defaultState
        self.currentState = self.defaultState

        # Create server
        server = SimpleXMLRPCServer((self.host, self.port),
                                    logRequests=False)
        server.register_introspection_functions()

        server.register_function(self.getState)
        server.register_function(self.changeStateTo)

        # Run the server
        server.serve_forever()

    def getState(self):
        return(self.currentState)

    def changeStateTo(self, newState):
        if newState not in self.states:
           raise ValueError, "newState {} is not in the list of allowed states {}".format(newState, self.states)

        sleep(2) # simulate the time it takes the hardware to change the state

        self.currentState = newState

        return self.getState()



