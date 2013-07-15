Signals
=======

What is this?
--------------

**A study of a distributed safety-critical system**

Out of curiosity, I wanted to explore methods to build a distributed system of railway signals that can monitor each other over the network to detect safety-critical situations.

For example, consider a railway switch that joins two tracks into one. The switch is protected by a signal on each track. To avoid collisions of trains, only one signal must show "green". Also, the switch must be moved towards the track the signal is showing "green" for.

The signal must only turn green if two constraints are met:

1. The other signal is showing "red"
2. The switch is in the correct position

The signal must also monitor if these constraints are still met during showing "green", and, as soon as it detects that one ore more constraints are violated, immediately fall back to a safe state, e.g. show "red".

**A graph representation of a railroad network**

I also implemented the *double vertex graph* as described by Markus Montigel (1992).

This graph makes it poosible to use pathfinding algorithmns on a railroad network.

Is it useful?
-------------

It depends on what you think is useful. The system is far from finished, and since I only started it to explore something it won't be finished.

You can't use this to control your model railroad

License
-------

The code is under the GPL, however, the individual files are not marked as such. 