from string import Template
from catapult.server.constants import WEBSOCKET_PREFIX


def get_ws_url(server_host, server_port):
    return Template('ws://{}:{}/websocket/$release_name{}'.format(
        server_host,
        server_port,
        WEBSOCKET_PREFIX
    ))
