import logging
from json import loads
from tornado.websocket import WebSocketHandler
from catapult.server.constants import INPUT_BEGIN, INPUT_END, INPUT_MESSAGE, WEBSOCKET_PREFIX
from catapult.server.constants import DEPLOY_PENDING
from catapult.server.constants import INVALID_RELEASE, RELEASE_DEPLOYED, INVALID_JSON, READ_ONLY, INVALID_REQUEST
from catapult.server.builders import event_error

output_connections = {}
logger = {}


class WebSocket(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(WebSocket, self).__init__(*args, **kwargs)

        self.is_input = False
        self.release_name = None

    def initialize(self, repository):
        self.repository = repository

    def check_origin(self, origin):
        return True

    def open(self, release_name):
        if release_name.endswith(WEBSOCKET_PREFIX):
            release_name = release_name[0: len(release_name) - len(WEBSOCKET_PREFIX)]
            self.is_input = True

        self.release_name = release_name

        release = self.repository.get_release(release_name)

        if not release:
            self.write_message(event_error(
                INVALID_RELEASE,
                'Release with name "{}" does not found'.format(release_name)
            ))

            self.close()

            return

        if release['status'] != DEPLOY_PENDING:
            self.write_message(event_error(
                RELEASE_DEPLOYED,
                'Release with name "{}" already deployed'.format(release_name)
            ))

            self.close()

            return

        add_connection(self)

        logging.info('open websocket with "{}" and is_input={}'.format(
            self.release_name,
            self.is_input
        ))

    def on_message(self, message):
        if not self.is_input:
            self.write_message(event_error(
                READ_ONLY,
                'This websocket only for read'
            ))

            return

        try:
            message = loads(message)
        except:
            self.write_message(event_error(
                INVALID_JSON,
                'An error occurred with parsing json'
            ))

            return

        if 'event' not in message:
            self.write_message(event_error(
                INVALID_REQUEST,
                'Field event not specified'
            ))

            return

        if message['event'] == INPUT_BEGIN:
            logger[self.release_name] = []

        if message['event'] == INPUT_MESSAGE:
            logger[self.release_name].append(message['payload'])

            send_messages(self.release_name, message['payload'])

        if message['event'] == INPUT_END:
            close_connections(self.release_name)

            del logger[self.release_name]

            self.close()

    def on_close(self):
        if not self.is_input:
            remove_connection(self)

        logging.info('close websocket with "{}" and is_input={}'.format(
            self.release_name,
            self.is_input
        ))


def send_messages(release_name, message):
    if release_name in output_connections:
        for connection in output_connections[release_name]:
            connection.write_message(message)


def close_connections(release_name):
    if release_name in output_connections:
        for connection in output_connections[release_name]:
            connection.close()

        del output_connections[release_name]


def add_connection(self):
    if self.is_input:
        return

    if self.release_name not in output_connections:
        output_connections[self.release_name] = []

    output_connections[self.release_name].append(self)

    if self.release_name in logger:
        for message in logger[self.release_name]:
            self.write_message(message)


def remove_connection(self):
    if self.release_name not in output_connections:
        return

    output_connections[self.release_name].remove(self)
