from catapult.deploy.constants import HOST_MAINTAIN
from catapult.library.maintain import execute_maintain


def phase(paths, storage, _, __, ssh, logger):
    hosts = storage.get_hosts(HOST_MAINTAIN)
    for host in hosts:
        ssh.execute_on_host(
            host,
            '{}/install.sh maintain'.format(paths.get('remote.release'))
        )

    logger.success('release installed on maintained servers')

    logger.info('start executing maintain commands')

    execute_maintain(
        storage,
        paths,
        ssh,
        storage.get('release.commands'),
        logger
    )

    logger.success('executing maintain commands completed')
