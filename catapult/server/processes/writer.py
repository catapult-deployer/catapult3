import logging
from catapult.server.constants import DEPLOY_PENDING
from catapult.server.killer import GracefulKiller


def writer(repository, write_queue):
    killer = GracefulKiller()

    while True:
        object = write_queue.get()

        if object['status'] == DEPLOY_PENDING:
            logging.info('write release {}'.format(object['name']))

            repository.insert_release(
                object['name'],
                object['request'],
                object['status'],
            )
        else:
            logging.info('update release {}'.format(object['name']))

            repository.update_release(
                object['name'],
                object['status'],
                object['logger'],
                object['time_end'],
            )

