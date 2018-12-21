import logging
import time
from catapult.loggers.server import Logger
from catapult.server.constants import DEPLOY_SUCCESS, DEPLOY_FAIL
from catapult.server.killer import GracefulKiller, GracefulKillerException


def worker(deploy, deploy_queue, write_queue, ws_template):
    try:
        killer = GracefulKiller()

        while True:
            request = deploy_queue.get()

            killer.work_started()

            logging.info('start execute request {}'.format(request['name']))

            ws_url = ws_template.substitute({
                'release_name': request['name']
            })

            logger = Logger(ws_url)

            logger.begin()

            status = DEPLOY_SUCCESS if deploy(request, logger) is True else DEPLOY_FAIL

            logging.info('request {} ended with status {}'.format(request['name'], status))

            logger.end()

            write_queue.put({
                'name': request['name'],
                'status': status,
                'time_end': int(time.time()),
                'logger': logger.get_logger(),
            })

            killer.work_finished()

            if killer.is_killed:
                break
    except GracefulKillerException:
        logging.info('worker process shutting down')
