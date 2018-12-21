from catapult.deploy.constants import HOST_WEB, HOST_BOT, HOST_ALL


def phase(paths, storage, _, __, ssh, logger):
    is_cluster_mode = storage.is_cluster_mode()

    if is_cluster_mode:
        logger.info('installing on cluster servers')

        hosts = storage.get_hosts(HOST_ALL)
        for host in hosts:
            logger.info('start installing on cluster host "{}"'.format(host))
            ssh.execute_on_host(
                host,
                '{}/install.sh all'.format(paths.get('remote.release'))
            )
            logger.success('installing on cluster host "{}" completed'.format(host))

        return

    logger.info('installing on cloud servers')

    for host_type in (HOST_BOT, HOST_WEB):
        hosts = storage.get_hosts(host_type)

        for host in hosts:
            logger.info('start installing "{}" host "{}"'.format(host_type, host))
            ssh.execute_on_host(
                host,
                '{}/install.sh {}'.format(
                    paths.get('remote.release'),
                    host_type
                )
            )
            logger.success('installing in "{}" host "{}" completed'.format(host_type, host))
