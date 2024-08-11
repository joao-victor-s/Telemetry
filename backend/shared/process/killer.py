import signal


class ProcessKiller:
    def __init__(self):
        self.die = False
        signal.signal(signal.SIGTERM, self.exit)
        signal.signal(signal.SIGINT, self.exit)

    def exit(self, signum, frame):
        self.die = True
