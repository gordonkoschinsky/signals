"""
Simple wrapper to use PubSub in a multithreaded environment, e.g.
when using a GUI with a mainloop in mian thread and worker threads that want to publish
some data back into the main thread.

Uses a threadsafe Queue.queue to collect messages

Use this module like the "pub" module in pubsub: Just import it in every module you want to
use it, it will automatically create a "ThreadSafePub" instance at import.

-- Example --
The worker threads can do this:

import threadsafepub as tpub

tpub.sendMessage("someTopic", somedata="Some Data")


The main thread can do this:

import threadsafepub as tpub

# in its idle callback:
mainThread_IdleCallback():
    tpub.poll()


Note:
The listeners just subscribe to pub.subscribe as usually! This module doesn't provide a
thread-safe subscription method. It just calls pub.sendMessage for all queued messages when
poll() is called.


More information:
http://groups.google.com/group/pypubsub_dev/browse_thread/thread/7f414e82f62d64b7

"""

from Queue import Queue
from pubsub import pub

class ThreadSafePub(object):
    def __init__(self):
        self.queue = Queue()

    def sendMessage(self, topic, **kwargs):
        self.queue.put((topic, kwargs))

    def poll(self):
        while not self.queue.empty():
            message = self.queue.get()
            kwargs = message[1]
            pub.sendMessage(message[0], **kwargs)



if __name__ == "__main__":
    # demo
    def observer(somedata):
        print "Observed: {}".format(somedata)

    pub.subscribe(observer, "mytopic")

    tpub = ThreadSafePub()

    tpub.sendMessage("mytopic", somedata="some data")
    tpub.sendMessage("myothertopic", somedata="no data")

    tpub.poll()

else:
    # create a ThreadSafePub instance

    _threadSafePub = ThreadSafePub()

    sendMessage = _threadSafePub.sendMessage
    poll        = _threadSafePub.poll
