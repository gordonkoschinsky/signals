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
