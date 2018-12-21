from catapult.library.renders import render_path, render_string
from catapult.modules.normalizers import normalize_systemd
from catapult.deploy.constants import HOST_ALL
from catapult.deploy.constants import REGISTER_CHECK, REGISTER_INSTALL, REGISTER_WEB_AND_BOT


class Module:
    def __init__(self, module_config, storage, paths, register, logger):
        self.module_config = module_config
        self.storage = storage
        self.paths = paths
        self.logger = logger

        register(REGISTER_INSTALL, REGISTER_WEB_AND_BOT, self.render_install())
        register(REGISTER_CHECK, REGISTER_WEB_AND_BOT, self.render_check())

    def render_check(self):
        path = '{}/systemd/check.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'storage': self.storage.get,
            'paths': self.paths.get,
        })

        return generated

    def render_install(self):
        path = '{}/systemd/install.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'release_path': self.paths.get('remote.release'),
            'service_name': 'catapult-{}'.format(self.storage.get('release.service')),
            'storage': self.storage.get,
            'paths': self.paths.get,
        })

        return generated

    def configure(self, config):
        config = normalize_systemd(config)
        hosts = self.storage.get_hosts(HOST_ALL)

        self.logger.info('configuring systemd unit file for all hosts: {}'.format(
            ', '.join(hosts))
        )

        configs = {}
        for host in hosts:
            self.storage.start_host(host)

            configs[host] = render(
                config,
                self.storage,
                self.paths
            )

            self.storage.finish_host()

        return configs


def render(config, storage, paths):
    path_environment = '{}/systemd/environment.j2'.format(
        paths.get('catapult.templates'),
    )

    path_unit = '{}/systemd/unit.j2'.format(
        paths.get('catapult.templates'),
    )

    environments = []
    for key, value in config['environments'].items():
        generated = render_path(path_environment, {
            'key': key,
            'value': value
        })

        environments.append(generated)

    execute = render_string(config['execute'], {
        'release_path': paths.get('remote.code'),
        'storage': storage.get,
        'paths': paths.get,
    })

    generated = render_path(path_unit, {
        'name': storage.get('release.service'),
        'user': storage.get('config.deploy.user'),
        'exec_start': execute,
        'environments': '\n'.join(environments),
    })

    return generated
