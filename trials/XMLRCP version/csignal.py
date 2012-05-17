from pubsub import Pub
from signalmessages import *
from threading import Thread
import rpctools
import socket

import logging

from time import sleep

class Signal(object):
    """
    Represent the "logical" signal in the main process
    The actual signal is a "dumb" process in server mode, which cn be told to change its
    state and  will answer its state when asked. It will run in "server mode".

    This logical signal holds the signal logic for interlocking etc.
    When initialized, it also starts a thread which communicates with the actual signal
    (socket client mode) and polls the state of the actual signal every second or so.
    The polled state is stored (with aquired lock!) into an instance variable.

    When the logical signal is asked to change its state, first it creates a thread
    (and terminates any old threads for the old state, if any, but only when
    the new state is established succesfully), then it asks all threats to lock
    (directly via a SafetyElementsRegistry["nameOfElement"] look up, that
    fetches the threat instance of a registry of all safety elements) in a required
    state. It will continue asking periodically, so if any of the threads change
    their state to differ from the required one, the signal will notice and fall
    back to a safe state.
    The asked threats will - if the polled state matches the required state - set
    their 'locked' instance variable and store the required state in an instance
    variable. The thread that periodically polls the actual signal will recognize
    the 'locked' flag, compare the actual with the required state and stores an error
    flag (maybe an exception) in an instance variable if actual and required states
    differ.

    TODO:

    - Switch to pyro.
    - Make the csignal polling thread set error flags if it can't reach the
    ssignal
    - Test RPC over network
    - Make main.py just setup all signals, no GUI
    - make csignal start a seperate thread with its own rpc-server to take commands
    from the GUI process. The GUI process also polls status and error information
    via RPC from csignal


    """
    def __init__(self, name, signalregistry):
        self.name = name
        self.signalregistry = signalregistry
        self.signalregistry[name] = self

        self.states = ("red", "green")
        self.curState = None
        self._setState("red")

        self.pollingActive = True

        self.requiredThreatStates = {}

        self.logger = logging.getLogger("signal.{}".format(self.name))

        self.rpc = rpctools.getRPCtimeoutProxy(host="zampano")

        thread = Thread(target=self.pollSignalState)
        thread.setDaemon(True)
        thread.start()

        # SUBSCRIBE TO EVENTS
        Pub.sub(self.name, self.requestGreen, SIG_REQ_GREEN)

    def pollSignalState(self):
        while self.pollingActive:
            sleep(1)
            try:
                print self.rpc.getState()
            except socket.error:
                pass
            # TODO flag error
            except socket.timeout:
                pass
            # TODO flag error

#        except Exception as inst:
#            print type(inst)     # the exception instance
#            print inst.args      # arguments stored in .args
#            print inst           # __str__ allows args to printed directly

    def addRequirement(self, state, threatName, reqThreatState):
        """ Define which state 'reqThreadState'
        a named threatening signal 'threatName' must be in
        for this signal to change to state 'state'
        """
        self._checkValidState(state)
        tmpDict = self.requiredThreatStates.setdefault(state, {})

        tmpDict[threatName] = reqThreatState

        self.requiredThreatStates[state] = tmpDict

    def requestGreen(self, message, data):
        print "logg", message, data
        self.logger.info("received a request to turn green")

        self.askThreatsToLock("green")
        self._setState("green")

    def askThreatsToLock(self, state):
        """Request a lock from all threads that are needed to be locked
        for this signal to turn to state 'state'
        """
        for threat, reqState in self.requiredThreatStates[state].items():
            self.logger.info("Asking {} to lock in state {}".format(threat, reqState))
            Pub.send(SIG_REQ_LOCK, threat, reqState)


    def _checkValidState(self, state):
        """Raises an exception ValueError if the state 'state' is
        not a valid  state for this signal.
        Returns None otherwise
        """
        if state not in self.states:
            raise(ValueError, "State not in the list of allowed states for this signal")

    def _setState(self, state):
        self._checkValidState(state)
        self.curState = state

    def __getattr__(self, name):
        if name == "curStateAbbr":
            return self.curState[0].upper()
        raise(AttributeError)


if __name__ == "__main__":
    signalregistry = {}
    s = Signal("S1", signalregistry)
    print(s.curStateAbbr)

    s.addRequirement("green", "s2", "red")
    s.addRequirement("green", "s3", "blue")
    print(s.requiredThreatStates)

    sleep(6)
