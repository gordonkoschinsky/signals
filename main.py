import csignal
from pubsub import pub


import logging



import signalregistry

signals = signalregistry.Registry()


s1 = csignal.Signal("S1", signals)
s1.configure()
s1.addRequirement("Ks1", "S2", "Hp0")
s1.configCompleted()


s2 = csignal.Signal("S2", signals)
s2.configure()
s2.configCompleted()
#s2._setState("Ks1")
#s2.locked = True

import gui_main
