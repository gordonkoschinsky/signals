"""
A XML RPC Transport Class that times out.

Use TimeoutTransport.set_timeout(n) to let the connection timeout after
n seconds.

Taken from:
http://stackoverflow.com/questions/2425799/timeout-for-xmlrpclib-client-requests
Answer by Alex Martelli
works only for Python 2.7!
"""

import xmlrpclib
import httplib

class TimeoutTransport(xmlrpclib.Transport):
    timeout = 10.0
    def set_timeout(self, timeout):
        self.timeout = timeout
    def make_connection(self, host):
        return httplib.HTTPConnection(host, timeout=self.timeout)

