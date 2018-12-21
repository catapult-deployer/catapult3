from os.path import exists
from catapult.deploy.constants import SERVER_WEB
from catapult.deploy.constants import REGISTER_CHECK, REGISTER_INSTALL, REGISTER_WEB
from catapult.modules.normalizers import normalize_nginx
from catapult.library.exceptions import ModuleException
from catapult.library.renders import render_path, render_string
from catapult.library.helpers import get_hosts


class Module:
    def __init__(self, module_config, storage, paths, register, logger):
        if 'template' not in module_config:
            raise ModuleException('You must set "template" parameter for module "nginx"!')

        self.module_config = module_config
        self.storage = storage
        self.paths = paths
        self.logger = logger

        register(REGISTER_CHECK, REGISTER_WEB, self.render_check_web())
        register(REGISTER_INSTALL, REGISTER_WEB, self.render_install_web())

    def render_check_web(self):
        path = '{}/nginx/check.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'storage': self.storage.get,
            'paths': self.paths.get,
        })

        return generated

    def render_install_web(self):
        path = '{}/nginx/install.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'release_path': self.paths.get('remote.release'),
            'file_name': 'catapult-{}'.format(self.storage.get('release.service')),
            'storage': self.storage.get,
            'paths': self.paths.get,
        })

        return generated

    def configure(self, config):
        config = normalize_nginx(config)
        servers = self.storage.get_servers(SERVER_WEB)

        if not servers or not config:
            self.logger.warning('there are not web servers')

            return

        self.logger.info('configuring web hosts: {}'.format(
            ', '.join(get_hosts(servers)))
        )

        template_path = '{}/{}'.format(
            self.paths.get('local.templates'),
            self.module_config['template']
        )

        if not exists(template_path):
            raise ModuleException(
                'Nginx template by path "{}" does not found'.format(template_path)
            )

        configs = {}
        for server in servers:
            host = server['host']

            self.storage.start_host(host)

            configs[host] = render(
                template_path,
                config,
                self.storage,
                self.paths
            )

            self.storage.finish_host()

        return configs


def render(template_path, config, storage, paths):
    path_parameter = '{}/nginx/parameter.j2'.format(
        paths.get('catapult.templates'),
    )

    path_location = '{}/nginx/location.j2'.format(
        paths.get('catapult.templates'),
    )

    locations = []
    for location in config['locations']:
        parameters = []

        for key, value in location['configs'].items():
            if type(value) is list:
                for item in value:
                    generated = render_path(path_parameter, {
                        'key': key,
                        'value': item
                    })

                    parameters.append(generated)
            else:
                generated = render_path(path_parameter, {
                    'key': key,
                    'value': value
                })

                parameters.append(generated)

        generated = render_path(path_location, {
            'modifier': location['modifier'],
            'match': location['match'],
            'parameters': '\n'.join(parameters),
            'storage': storage.get,
            'paths': paths.get,
        })

        locations.append(generated)

    index_files = config['index_files']
    if type(index_files) is list:
        index_files = ' '.join(index_files)

    root = render_string(config['root'], {
        'release_path': paths.get('remote.code'),
        'storage': storage.get,
        'paths': paths.get,
    })

    item = render_path(template_path, {
        'root': root,
        'index_files': index_files,
        'locations': '\n'.join(locations),
        'storage': storage.get,
        'paths': paths.get,
    })

    path_nginx = '{}/nginx/nginx.j2'.format(
        paths.get('catapult.templates'),
    )

    generated = render_path(path_nginx, {
        'item': item,
        'storage': storage.get,
        'paths': paths.get,
    })

    return generated
