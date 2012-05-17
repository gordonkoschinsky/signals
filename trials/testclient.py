import Pyro4
from time import sleep
import socket



Pyro4.config.HMAC_KEY = "eea80c6848ddc1f78b37d882b5f837b32064e847a7cb82b54a459a76da5c2394"

s1 = Pyro4.Proxy("PYRONAME:signal.S1")
s1._pyroTimeout = 2
Pyro4.config.COMMTIMEOUT = 0.5

print s1.getState()
try:
    print s1.changeStateTo("Ks1")
except Pyro4.errors.TimeoutError:
    print "Timed out."

try:
    print s1.getState()
except socket.timeout:
    print "Timed out."


print s1.getState()
#sleep(1)
print s1.getState()
#sleep(0.5)
print s1.getState()
#sleep(1)
print s1.getState()

try:
    print s1.changeStateTo("Hp0")
except Pyro4.errors.TimeoutError:
    print "Timed out."

    print s1.changeStateTo("Ks2")
