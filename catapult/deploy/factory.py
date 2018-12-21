import importlib
from catapult.deploy.ssh import Ssh
from catapult.deploy.paths import Paths
from catapult.deploy.notifier import Notifier
from catapult.deploy.recipes import Recipes
from catapult.deploy.storage import Storage
from catapult.deploy.locker import Locker
from catapult.deploy.blocker import Blocker
from catapult.deploy.constants import HOST_ALL, PHASES
from catapult.deploy.logger import Logger
from catapult.library.helpers import get_place
from catapult.library.exceptions import BlockerException
from catapult.deploy.constants import STATE_BEFORE, STATE_AFTER


def factory(project_path, config, services):
    def deploy(request, logger):
        logger = Logger(logger)

        try:
            place, storage, ssh, paths, notifier, locker, blocker, recipes = get_instances(
                project_path,
                config,
                services,
                request,
                logger
            )
        except Exception as error:
            logger.error('An error occurred with initializing: {}'.format(error))

            return False

        try:
            for phase in PHASES:
                logger.phase(
                    phase,
                    request['service'],
                    request['branch'],
                    request['place'],
                )

                recipes.execute(STATE_BEFORE, phase)

                imported_module = importlib.import_module('catapult.deploy.phases.{}'.format(phase))

                imported_module.phase(
                    paths,
                    storage,
                    locker,
                    blocker,
                    ssh,
                    logger
                )

                recipes.execute(STATE_AFTER, phase)

            notifier.notify(True)
        except Exception as error:
            logger.error(error)

            # release local lock
            if not isinstance(error, BlockerException):
                blocker.release_lock()

            try:
                notifier.notify(False)
            except Exception as error:
                logger.error('an error occurred with notifying: "{}"'.format(error))

            return False

        return True

    return deploy


def get_instances(project_path, config, services, request, logger):
    place = get_place(
        services,
        request['service'],
        request['place'],
    )

    storage = Storage(
        config,
        place,
        request
    )

    ssh = Ssh(
        config['deploy']['ssh']['user'],
        config['deploy']['ssh']['key_file'],
        storage.get_hosts(HOST_ALL),
        logger
    )

    paths = Paths(
        project_path,
        request['service'],
        config['deploy']['deploy_path'],
        request['name'],
    )

    notifier = Notifier(
        place['notifications'],
        request,
        logger
    )

    locker = Locker(
        paths,
        storage,
        ssh,
        logger
    )

    blocker = Blocker(
        paths.get('local.releases_folder'),
        request['place'],
        request['name']
    )

    recipes = Recipes(
        storage,
        paths,
        ssh,
        logger
    )

    return place, storage, ssh, paths, notifier, locker, blocker, recipes
