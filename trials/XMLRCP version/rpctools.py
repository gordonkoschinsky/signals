import xmlrpclib
import rpctimeouttransport


def getRPCtimeoutProxy(host='127.0.0.1', port='8000', timeout=3.0):
    """Returns a XML RPC Proxyserver with a timeout transport.
    """
    t = rpctimeouttransport.TimeoutTransport()
    t.set_timeout(timeout)

    return xmlrpclib.ServerProxy('http://{}:{}'.format(host, port), transport=t)
