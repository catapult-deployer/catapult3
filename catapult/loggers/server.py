import logging
from websocket import create_connection
from catapult.server.constants import INPUT_BEGIN, INPUT_MESSAGE, INPUT_END
from catapult.server.builders import event_input


class Logger:
    def __init__(self, ws_url):
        self.logger = []
        self.ws = create_connection(ws_url)

    def begin(self):
        send_socket(
            self.ws,
            event_input(
                INPUT_BEGIN,
            )
        )

    def event(self, level, message):
        payload = {
            'level': level,
            'message': message,
        }

        self.logger.append(payload)

        send_socket(
            self.ws,
            event_input(
                INPUT_MESSAGE,
                payload
            )
        )

    def get_logger(self):
        return self.logger

    def end(self):
        send_socket(
            self.ws,
            event_input(
                INPUT_END,
            )
        )


def send_socket(connection, data):
    try:
        connection.send(data)
    except Exception as error:
        logging.error('an error "{}" occurred with sending data to socket "{}"'.format(error, data))
