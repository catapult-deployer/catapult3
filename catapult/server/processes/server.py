import logging
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.web import Application
from catapult.server.routes.get_release import GetRelease
from catapult.server.routes.post_release import PostRelease
from catapult.server.routes.websocket import WebSocket
from catapult.server.killer import GracefulKiller, GracefulKillerException


def server(config, services, repository, deploy_queue, write_queue):
    try:
        killer = GracefulKiller()

        server_host = config['server']['host']
        server_port = config['server']['port']
        token = config['server']['token']

        application = Application([
            (r'/releases', PostRelease, dict(
                token=token,
                services=services,
                deploy_queue=deploy_queue,
                write_queue=write_queue,
            )),
            (r'/releases/(.*)', GetRelease, dict(
                token=token,
                repository=repository
            )),
            (r'/websocket/(.*)', WebSocket, dict(
                repository=repository
            )),
        ])

        logging.info('trying start server on {}:{}'.format(server_host, server_port))

        http_server = HTTPServer(application)
        http_server.listen(server_port, server_host)

        IOLoop.current().start()
    except GracefulKillerException:
        logging.info('server process shutting down')
