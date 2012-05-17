class Registry(object):
    def __init__(self):
        self.signals = {}

    def add(self, signal):
        self.signals[signal.name] = signal

    def get(self, signalName):
        return self.signals[signalName]
    
