from os import makedirs
from catapult.deploy.constants import SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN


def phase(paths, storage, _, __, ___, logger):
    logger.success('release started by name "{}"'.format(storage.get('release.name')))
    makedirs(paths.get('local.code'))

    place = storage.get('place')

    # show list of recipes
    if place['recipes']:
        for recipe in place['recipes']:
            logger.info('recipe "{}" will be used'.format(recipe))

    # show list of servers
    if 'cloud' in place:
        logger.info('used "cloud mode" for deploying')

        for host_type in (SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN):
            if host_type in place['cloud']:
                for item in place['cloud'][host_type]:
                    logger.info(
                        '"{}" host "{}" will be used'.format(
                            host_type,
                            item['host']
                        )
                    )
    else:
        logger.info('used "cluster mode" for deploying')

        for server in place['cluster']:
            logger.info(
                'host "{}" will be used'.format(
                    server['host']
                )
            )

    # show list of modules
    if place['modules']:
        for module in place['modules']:
            logger.info('module "{}" will be used'.format(module))
