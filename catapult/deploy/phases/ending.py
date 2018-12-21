import time


def phase(_, storage, locker, blocker, ssh, logger):
    # release remote lock
    logger.info('try to release remote locks')
    locker.release_lock()
    logger.success('remote lock released successfully')

    # local local lock
    logger.info('try to release local lock')
    blocker.release_lock()
    logger.success('local lock released successfully')

    # close ssh connections
    logger.info('try to close all ssh connections')
    ssh.close()
    logger.success('ssh connections closed successfully')

    time_spend = round(time.time() - storage.get('release.time_start'), 2)
    logger.info('deployed in {}s'.format(time_spend))
