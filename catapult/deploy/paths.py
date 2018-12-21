from os.path import abspath, dirname, join
from catapult.library.helpers import get_nested
from catapult.library.exceptions import InvalidParameterException


class Paths:
    def __init__(self, project_path, service, deploy_path, release_name):
        # generated absolute path to catapult project
        catapult_folder = abspath(join(dirname(__file__), '../'))

        self.paths = {
            'catapult': {
                'templates': '{}/templates'.format(
                    catapult_folder
                ),
                'modules': '{}/modules'.format(
                    catapult_folder
                ),
            },
            'local': {
                'project_path': project_path,
                'recipes': '{}/recipes'.format(
                    project_path
                ),
                'services': '{}/services'.format(
                    project_path
                ),
                'templates': '{}/templates'.format(
                    project_path
                ),
                'releases_folder': '{}/releases/{}'.format(
                    project_path,
                    service
                ),
                'release': '{}/releases/{}/{}'.format(
                    project_path,
                    service,
                    release_name
                ),
                'configs': '{}/releases/{}/{}/configs'.format(
                    project_path,
                    service,
                    release_name,
                ),
                'code': '{}/releases/{}/{}/code'.format(
                    project_path,
                    service,
                    release_name,
                ),
                'builds': '{}/releases/{}/{}/builds'.format(
                    project_path,
                    service,
                    release_name,
                ),
                'shared': '{}/releases/{}/{}/shared'.format(
                    project_path,
                    service,
                    release_name,
                ),
            },

            'remote': {
                'service_folder': '{}/{}'.format(
                    deploy_path,
                    service
                ),
                'releases_folder': '{}/{}/releases'.format(
                    deploy_path,
                    service
                ),
                'release': '{}/{}/releases/{}'.format(
                    deploy_path,
                    service,
                    release_name
                ),
                'code': '{}/{}/releases/{}/code'.format(
                    deploy_path,
                    service,
                    release_name
                ),
            }
        }

    def get(self, path, default=None):
        """
            catapult.templates
            catapult.modules

            local.project_path
            local.recipes
            local.services
            local.templates
            local.releases_folder
            local.release
            local.configs
            local.code
            local.builds
            local.shared

            remote.service_folder
            remote.releases_folder
            remote.release
            remote.code
        """
        try:
            return get_nested(path, self.paths)
        except InvalidParameterException as error:
            if default is None:
                raise error

            return default
