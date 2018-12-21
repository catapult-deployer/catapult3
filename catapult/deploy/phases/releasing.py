from catapult.deploy.constants import HOST_ALL


def phase(paths, storage, _, __, ssh, logger):
    logger.info('start creating folder for release')
    ssh.execute_on_hosts('mkdir -p {}'.format(
        paths.get('remote.release')
    ))
    logger.success('folder "{}" for release created'.format(paths.get('remote.release')))

    hosts = storage.get_hosts(HOST_ALL)

    for host in hosts:
        ssh.move_on_host(
            host,
            '{}/{}.tar.gz'.format(paths.get('local.builds'), host),
            '{}/archive.tar.gz'.format(paths.get('remote.release'))
        )
        logger.success('tar ball catapulted', host)

    logger.info('start extracting tar balls on all hosts')
    ssh.execute_on_hosts('cd {} && tar -xf archive.tar.gz'.format(
        paths.get('remote.release'))
    )
    logger.success('tar balls extracted')

    ssh.execute_on_hosts('rm {}/archive.tar.gz'.format(paths.get('remote.release')))
