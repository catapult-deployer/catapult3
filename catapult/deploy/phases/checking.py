from catapult.deploy.constants import HOST_WEB, HOST_BOT, HOST_MAINTAIN, HOST_ALL


def phase(paths, storage, _, __, ssh, logger):
    # check date for hosts
    ssh.execute_on_hosts('date')

    # move check file on hosts
    local_path = '{}/check.sh'.format(paths.get('local.release'))
    remote_path = '/tmp/check_{}.sh'.format(storage.get('release.name'))

    ssh.move_on_hosts(
        local_path,
        remote_path
    )

    ssh.execute_on_hosts('chmod +x {}'.format(remote_path))

    is_cluster_mode = storage.is_cluster_mode()
    if is_cluster_mode:
        logger.info('check cluster servers')

        hosts = storage.get_hosts(HOST_ALL)
        for host in hosts:
            logger.info('start checking cluster host "{}"'.format(host))
            ssh.execute_on_host(host, '{} all'.format(remote_path))
            logger.success('checking cluster host "{}" completed'.format(host))

        return

    logger.info('check cloud servers')

    for host_type in (HOST_WEB, HOST_BOT, HOST_MAINTAIN):
        hosts = storage.get_hosts(host_type)

        for host in hosts:
            logger.info('start checking "{}" host "{}"'.format(host_type, host))
            ssh.execute_on_host(
                host,
                '{} {}'.format(
                    remote_path,
                    host_type
                )
            )
            logger.success('checking "{}" host "{}" completed'.format(host_type, host))
