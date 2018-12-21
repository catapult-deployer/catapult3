import logging
from signal import signal, SIGINT, SIGTERM


class GracefulKiller:
    def __init__(self, is_disabled=False):
        self.is_killed = False
        self.is_worked = False

        handler = self.stub_handler if is_disabled else self.signal_handler

        signal(SIGINT, handler)
        signal(SIGTERM, handler)

    def signal_handler(self, signum, _):
        logging.info('handled signal "{}"'.format(signum))

        self.is_killed = True

        if not self.is_worked:
            raise GracefulKillerException()

    def stub_handler(self, signum, _):
        logging.info('handled stub signal "{}"'.format(signum))

    def work_started(self):
        self.is_worked = True

    def work_finished(self):
        self.is_worked = False


class GracefulKillerException(Exception):
    pass
