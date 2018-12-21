from catapult.library.renders import render_path, render_string
from catapult.library.helpers import get_hosts
from catapult.modules.balancer import balanced_by_host
from catapult.modules.normalizers import normalize_crons
from catapult.deploy.constants import SERVER_BOT
from catapult.deploy.constants import REGISTER_CHECK, REGISTER_INSTALL, REGISTER_BOT


class Module:
    def __init__(self, module_config, storage, paths, register, logger):
        self.module_config = module_config
        self.storage = storage
        self.paths = paths
        self.logger = logger

        register(REGISTER_CHECK, REGISTER_BOT, self.render_check_bot())
        register(REGISTER_INSTALL, REGISTER_BOT, self.render_install_bot())

    def render_check_bot(self):
        path = '{}/crontab/check.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'storage': self.storage.get,
            'paths': self.paths.get,
        })

        return generated

    def render_install_bot(self):
        path = '{}/crontab/install.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'release_path': self.paths.get('remote.release'),
            'file_name': 'catapult-{}'.format(self.storage.get('release.service')),
            'storage': self.storage.get,
            'paths': self.paths.get
        })

        return generated

    def configure(self, config):
        crons = normalize_crons(config)
        servers = self.storage.get_servers(SERVER_BOT)

        if not servers or not config:
            self.logger.warning('there are not bot servers')

            return

        self.logger.info('configuring bot hosts: {}'.format(
            ', '.join(get_hosts(servers)))
        )

        crontab = get_crontab(self.storage, crons, servers)

        # render
        configs = {}
        for host in crontab:
            self.storage.start_host(host)

            configs[host] = render(
                crontab[host],
                self.storage,
                self.paths
            )

            self.storage.finish_host()

        return configs


def get_crontab(storage, crons, servers):
    crontab = {}

    # cluster mode
    if storage.is_cluster_mode():
        for server in servers:
            crontab[server['host']] = crons

        return crontab

    # cloud mode
    balancing = balanced_by_host(crons, servers)

    for server in servers:
        crontab[server['host']] = []

        for cron in balancing[server['host']]:
            crontab[server['host']].append(cron)

    return crontab


def render(crons, storage, paths):
    items = []

    path_item = '{}/crontab/item.j2'.format(
        paths.get('catapult.templates'),
    )

    for cron in crons:
        command = render_string(cron['command'], {
            'release_path': paths.get('remote.code'),
            'storage': storage.get,
            'paths': paths.get,
        })

        item = render_path(path_item, {
            'minutes': str(cron['planning']['minutes']),
            'hours': str(cron['planning']['hours']),
            'dom': str(cron['planning']['dom']),
            'mon': str(cron['planning']['mon']),
            'dow': str(cron['planning']['dow']),
            'command': command,
            'user': storage.get('config.deploy.user'),
            'storage': storage.get,
            'paths': paths.get,
        })

        items.append(item)

    path_crontab = '{}/crontab/crontab.j2'.format(
        paths.get('catapult.templates'),
    )

    generated = render_path(path_crontab, {
        'items': '\n\n'.join(map(str, items)),
        'storage': storage.get,
        'paths': paths.get,
    })

    return generated
