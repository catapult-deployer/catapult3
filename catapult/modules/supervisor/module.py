from catapult.deploy.constants import REGISTER_CHECK, REGISTER_INSTALL, REGISTER_BOT
from catapult.deploy.constants import SERVER_BOT
from catapult.library.renders import render_path, render_string
from catapult.library.helpers import get_hosts
from catapult.modules.library import get_balancing_demons, get_mirroring_demons
from catapult.modules.normalizers import normalize_supervisor
from catapult.modules.constants import BOT_MIRRORING
from catapult.modules.balancer import balanced_by_host


class Module:
    def __init__(self, module_config, storage, paths, register, logger):
        self.module_config = module_config
        self.storage = storage
        self.paths = paths
        self.logger = logger

        register(REGISTER_CHECK, REGISTER_BOT, self.render_check_bot())
        register(REGISTER_INSTALL, REGISTER_BOT, self.render_install_bot())

    def render_check_bot(self):
        path = '{}/supervisor/check.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'storage': self.storage.get,
            'paths': self.paths.get
        })

        return generated

    def render_install_bot(self):
        path = '{}/supervisor/install.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'release_path': self.paths.get('remote.release'),
            'file_name': 'catapult-{}'.format(self.storage.get('release.service')),
            'service_name': self.storage.get('release.service'),
            'storage': self.storage.get,
            'paths': self.paths.get
        })

        return generated

    def configure(self, config):
        demons = normalize_supervisor(config)
        servers = self.storage.get_servers(SERVER_BOT)

        if not servers or not config:
            self.logger.warning('there are not bot servers')

            return

        self.logger.info('configuring bot hosts: {}'.format(
            ', '.join(get_hosts(servers)))
        )

        supervisor = get_supervisor(
            demons,
            servers,
            self.storage.is_cluster_mode()
        )

        configs = {}
        for host in supervisor:
            self.storage.start_host(host)

            configs[host] = render(
                supervisor[host],
                self.storage,
                self.paths
            )

            self.storage.finish_host()

        return configs


def get_supervisor(demons, servers, is_cluster_mode):
    supervisor = {}

    balancing_demons = get_balancing_demons(demons)
    mirroring_demons = get_mirroring_demons(demons)

    # cluster mode
    if is_cluster_mode:
        for server in servers:
            supervisor[server['host']] = []

            for demon in mirroring_demons:
                supervisor[server['host']].append(demon)

            for demon in balancing_demons:
                supervisor[server['host']].append(demon)

        return supervisor

    # cloud mode
    balanced = balanced_by_host(balancing_demons, servers)

    # compose demons by hosts
    for server in servers:
        supervisor[server['host']] = []

        for demon in mirroring_demons:
            supervisor[server['host']].append(demon)

        for demon in balanced[server['host']]:
            supervisor[server['host']].append(demon)

    return supervisor


def render(demons, storage, paths):
    items = []

    path_item = '{}/supervisor/item.j2'.format(
        paths.get('catapult.templates'),
    )

    for demon in demons:
        command = render_string(demon['command'], {
            'release_path': paths.get('remote.code'),
            'storage': storage.get,
            'paths': paths.get
        })

        numprocs = 1
        process_name = '{}_{}'.format(
            storage.get('release.service'),
            demon['name'],
        )

        if demon['type'] == BOT_MIRRORING:
            numprocs = demon['instances']
            process_name = '%(program_name)s_%(process_num)02d'

        item = render_path(path_item, {
            'service': storage.get('release.service'),
            'program': demon['name'],
            'process_name': process_name,
            'command': command,
            'user': storage.get('config.deploy.user'),
            'numprocs': str(numprocs),
            'storage': storage.get,
            'paths': paths.get
        })

        items.append(item)

    path_supervisor = '{}/supervisor/supervisor.j2'.format(
        paths.get('catapult.templates'),
    )

    generated = render_path(path_supervisor, {
        'items': '\n\n'.join(map(str, items)),
        'storage': storage.get,
        'paths': paths.get
    })

    return generated
