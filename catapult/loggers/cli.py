from blessings import Terminal
from catapult.deploy.constants import LOGGER_ERROR, LOGGER_INFO, LOGGER_PHASE, LOGGER_SUCCESS, LOGGER_WARNING

terminal = Terminal()


class Logger:
    @staticmethod
    def event(level, message):
        terminal_message = ''

        if level == LOGGER_INFO:
            terminal_message = terminal.cyan(message)

        if level == LOGGER_ERROR:
            terminal_message = terminal.red(message)

        if level == LOGGER_SUCCESS:
            terminal_message = terminal.green(message)

        if level == LOGGER_WARNING:
            terminal_message = terminal.yellow(message)

        if level == LOGGER_PHASE:
            terminal_message = terminal.bold_white(message)

        print(terminal_message)
