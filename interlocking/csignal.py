from pubsub import pub
from threading import Thread
from threading import Lock
import Pyro4

import logging

from time import sleep

from signalexceptions import *

Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"
#Pyro4.config.COMMTIMEOUT = 0.5
#Pyro4.config.POLLTIMEOUT = 0.5



class Signal(object):
    """
    Represents the "logical" signal in the main process
    The actual signal is a "dumb" process in "server mode", which can be told to change its
    state and will answer its state when asked.

    This logical signal holds the signal logic for interlocking etc.
    When initialized, it also starts a thread which communicates with the actual signal
    ("client mode") and polls the state of the actual signal every second or so.
    The polled state is stored (with aquired lock!) into an instance variable.
    If the polled state differs from the logical state, the signal is flagged as
    erroneous.

    When the logical signal is asked to change its state, first it creates a thread
    (and terminates any old threads for the old state, if any, but only when
    the new state is established succesfully), then it checks if all threats are in a required
    state. It will continue asking periodically, so if any of the threats change
    their state to differ from the required one, the signal will notice and fall
    back to its safe state.



    """
    def __init__(self, name, signals):
        """Init the signal.

        Note: This won't "activate" the signal. It first must be configured
        using configure() and addRequirements() and made active with
        onfigCompleted().
        """
        self.name = name
        self.signals = signals

        # the logical state. Must be configured first by Signal.configure()
        self.states = ()
        self.safeState = ""
        self.curState = None
        self.locked = False
        self.signalError = True
        self.errorException = None

        self.requiredThreatStates = {}

        self.active = False

        self.DEBUG_STATEREMOTECONTROLLED = False # if True, no error is flagged when the remote
                                                # signal changes its state without being
                                                # told to, but the state in this instance
                                                # is silently changed to the remote one.
                                                # So debugging is possible via gui.

        # THREADS
        self.watchdog = None
        self.pollingActive = False
        self.watchdogActive = False
        self.tlock = Lock()


        self.logger = logging.getLogger("signal.{}".format(self.name))

        # the "real world" counterpart of this signal in the field
        self.ssignal = Pyro4.Proxy("PYRONAME:signal.{}".format(self.name))
        self.ssignal._pyroTimeout = 1


        # register this signal in the registry
        self.signals.add(self)

    def configure(self, states=("Hp0", "Ks1") , safeState="Hp0"):
        """Set all states the signal can be in,
        and out of these the state that is considered "safe" and thus is used
        as a default and as a fallback if any error occurs.

        Defaults to configure a Deutsche Bahn KS-Hauptsignal
        """
        if self.active:
            raise SignalConfigError, "configuration of signal {} already completed".format(self.name)
        self.states = states
        self._checkValidState(safeState)
        self.safeState = safeState

    def configCompleted(self):
        """Lock the signal's configuration.
        No changes can be made anymore via Signal.configure() and
        Signal.addRequirement().

        Sets the default, save state and starts the communication with the
        field signal, and subsribes to events to get commands from the controller
        and from other signal. In other words: Activates the signal.

        Note: There is no sanity check! Make sure that configure() has really
        been called with sane values!
        """
        self.active = True

        self._setState(self.safeState)
        self.signalError = False

        self.pollingActive = True
        thread = Thread(target=self.pollSignalState)
        thread.setDaemon(True)
        self.logger.debug("Watchdog thread starting...")
        thread.start()
        self.logger.debug("Watchdog thread started")
        # SUBSCRIBE TO EVENTS
        pub.subscribe(self.onKs1Requested, "signal.{}.requestKs1".format(self.name))
        pub.subscribe(self.onResetRequested, "signal.{}.requestReset".format(self.name))

    def addRequirement(self, state, threatName, reqThreatState):
        """ Define which state 'reqThreadState'
        a named threatening signal 'threatName' must be in
        for this signal to change to state 'state'
        """
        if self.active:
            raise SignalConfigError, "configuration of signal {} already completed".format(self.name)
        self._checkValidState(state)
        tmpDict = self.requiredThreatStates.setdefault(state, {})
        tmpDict[threatName] = reqThreatState
        self.requiredThreatStates[state] = tmpDict


    ############################################################################
    # Threads

    def pollSignalState(self):
        """Periodically poll the state of the field signal

        Runs in a thread that is started as soon as the signal is turned active.

        Publishes a state datagram on every run via pubsub
        """
        while self.pollingActive:
            self.logger.debug("Polling state")
            self.pollState = self._remoteCall(self.ssignal.getState)
            self.logger.debug("Polling done")
            # Publish our state, regardless of pollState
            pub.sendMessage("signal.{}.stateDatagram".format(self.name),
                            datagram= {
                                "state":self.curState,
                                #"pollState":self.pollState,
                                "signalError":self.signalError #,
                                #"errorException":self.errorException
                            }
                            )

            if isinstance(self.pollState, SignalError):
                # Connection faulty, error already set by _remoteCall, skip
                continue
            if not self.pollState == self.curState:
                if not self.DEBUG_STATEREMOTECONTROLLED:
                    # if the remote state changes, we silently set the logical state to the remote one for debugging
                    # normally, this means the remote signal is faulty and  we must flag an error
                    self._setError(SignalError("Signal state not consistent. IS: {} SHOULD: {}".format(self.pollState, self.curState)))
                else:
                    # debugging, set state to the remote state
                    self.curState = self.pollState
            sleep(1)

    def threatStateWatchdog(self, state):
        """Check if all threats for state 'state' are still in the required
        state.

        If not, fallback to Signal.safeState and terminate
        """
        self.logger.debug("Starting watchdog for state {}".format(state))
        while self.watchdogActive:
            if not self.checkThreatSafeStateFor(state):
                # at least one threat is not safe anymore: fallback to safe state
                self.tlock.acquire()
                try:
                    self._setState(self.safeState)
                    self.watchdogActive = False
                finally:
                    self.tlock.release()
            sleep(1)
        self.logger.debug("Terminating watchdog for state {}".format(state))

    ############################################################################
    # EVENT HANDLERS

    def onKs1Requested(self):
        self._checkActive()
        self.logger.info("received a request to turn to Ks1")
        if self.curState == "Ks1":
            self.logger.debug("is already in the requested state Ks1")
            return
        if self.checkThreatSafeStateFor("Ks1"):
            # Signal old watchdog to end
            self.watchdogActive = False
            # Wait for watchdog to terminate
            if self.watchdog:
                self.watchdog.join()
            # create new watchdog to call checkThreatSafe again and again
            self.logger.debug("Starting watchdog")
            thread = Thread(target=self.threatStateWatchdog, args=("Ks1",))
            self.watchdog = thread
            self.watchdogActive = True
            thread.setDaemon(True)
            thread.start()

            self._setState("Ks1")

    def onResetRequested(self):
        self._resetError()

    ############################################################################
    # COMMAND METHODS

    def requestSafeState(self, reqState):
        self._checkActive()
        self._checkValidState(reqState)

        if self.signalError:
            return "ERROR"
        elif self.curState == reqState:
            return "OK"
        elif not self.curState == reqState:
            if self.locked:
                return "LOCKEDOTHERSTATE"
            else:
                return "OTHERSTATE"
        return "ERROR"

    ############################################################################
    #

    def checkThreatSafeStateFor(self, state):
        """Checks if all threads that are needed to be in a certain state
        for this signal to turn to state 'state' are indeed in this state
        """
        for threatName, reqState in self.requiredThreatStates[state].items():
            # check us for error, if any, publish mesage and quit
            if self.signalError:
                self.logger.error("Signal {} is erroneous. Error:{}".format(self.name, self.errorException))
                return False
            self.logger.info("Asking {} if it's in state {}".format(threatName, reqState))
            response = self.signals.get(threatName).requestSafeState(reqState)
            # possible responses:
            # OK (signal is in the right state)
            # LOCKEDOTHERSTATE (signal is locked in a different state than the requested one)
            # OTHERSTATE (signal is in a different state than the requested one, but unlocked)
            # ERROR (signal is unoperative)
            if response is not "OK":
                if response is "OTHERSTATE":
                    # TODO: in automode, ask signal to turn its state
                    # TODO: set timer to repeat this method after 10 seconds
                    self.logger.debug("Signal {} is not in the required state {}. Auto change possible.".format(threatName, reqState))
                    return False
                else:
                    self.logger.error("Signal {} is not in the required state {}. Response:{}".format(threatName, reqState, response))
                    # TODO: publish error for the GUI to display
                    return False
        # still here means all threats are safe
        return True

    def _checkValidState(self, state):
        """Raises an exception ValueError if the state 'state' is
        not a valid  state for this signal.
        Returns None otherwise
        """
        if state not in self.states:
            raise(ValueError, "State {} not in the list of allowed states for this signal".format(state))

    def _checkActive(self):
        """Raises an exception SignalConfigError if this signal is not active
        """
        if not self.active:
            raise SignalConfigError("Signal {} is not active.".format(self.name))

    def _remoteCall(self, callee, *args, **kwargs):
        response = False
        try:
            response = callee(*args, **kwargs)
        except Pyro4.errors.CommunicationError:
            response = self._setError(SignalFieldConnectionError("Connection error with remote signal."))
        except Pyro4.errors.TimeoutError:
            response = self._setError(SignalFieldConnectionError("Connection to remote signal timed out."))
        #except socket.ConnectionClosedError:
        #    self._setError(SignalFieldConnectionError("Connection closed by remote signal."))
        except Pyro4.errors.NamingError as e:
            response= self._setError(SignalFieldConnectionError("Naming error: {}".format(e)))
        except Exception as e:
            response = e
        self.logger.debug("Response from remote call is {}".format(response))
        return response

    def _setState(self, state):
        self._checkValidState(state)
        self.curState = state
        self.logger.info("Signal {} changed state to {}.".format(self.name, state))
        pub.sendMessage("signal.{}.stateChanged".format(self.name), state=state)
        self._remoteCall(self.ssignal.changeStateTo, self.curState)

    def _setError(self, exception):
        self.tlock.acquire()
        try:
            self.signalError = True
            self.errorException = exception
            self.logger.error("signal {} is erroneous! {}".format(self.name, self.errorException))
        finally:
            self.tlock.release()
        return exception
#        except Exception as inst:
#            print type(inst)     # the exception instance
#            print inst.args      # arguments stored in .args
#            print inst           # __str__ allows args to printed directly

    def _resetError(self):
        self.tlock.acquire()
        try:
            self.signalError = False
            self.errorException = None
            self.logger.info("Trying to reset signal {} error!".format(self.name))
        finally:
            self.tlock.release()


if __name__ == "__main__":
    import signalregistry
    s = Signal("S1", signalregistry.Registry())

    s.configure()
    s.addRequirement("Ks1", "s2", "Hp0")
    s.addRequirement("Ks1", "s3", "blue")
    print(s.requiredThreatStates)

    s.configCompleted()
    sleep(6)
    print s.errorException
    print s.signalError
