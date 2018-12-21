import re
import time
from catapult.deploy.constants import LOGGER_ERROR, LOGGER_INFO, LOGGER_PHASE, LOGGER_SUCCESS, LOGGER_WARNING


class Logger:
    def __init__(self, logger):
        self.logger = logger

    def info(self, message, host=None):
        self.logger.event(LOGGER_INFO, draw(message, host))

    def error(self, message, host=None):
        self.logger.event(LOGGER_ERROR, draw(cut_message(message), host))

    def success(self, message, host=None):
        self.logger.event(LOGGER_SUCCESS, draw(cut_message(message), host))

    def warning(self, message, host=None):
        self.logger.event(LOGGER_WARNING, draw(message, host))

    def phase(self, phase, service, branch, place):
        message = '{} [service: {} | branch: {} | place: {}]'.format(
            phase.upper(),
            service.lower(),
            branch.lower(),
            place.lower()
        )

        self.logger.event(LOGGER_PHASE, draw(message + ' ' + '*' * (150 - len(message)), None))


def draw(message, host):
    if host:
        message = '[{}] {}'.format(host, message)

    message = '[{}] {}'.format(time.strftime('%H:%M:%S'), message)

    return message


def cut_message(message):
    message = str(message)

    message = re.sub('\u001b\[[0-9]*[A-K]', '', message)
    message = re.sub('\u001b\[[0-9;]*m', '', message)

    message = message.strip()

    if len(message) > 250:
        return message[0: 250] + '...'

    return message.strip()
