def phase(_, __, locker, blocker, ___, logger):
    # acquire local lock
    logger.info('try to acquire local lock')
    blocker.acquire_lock()
    logger.success('local lock acquired successfully')

    # remote lock
    logger.info('try to acquire remote locks')
    locker.acquire_lock()
    logger.success('remote locks acquired successfully')
