from json import dumps
from catapult.library.renders import render_path, render_string
from catapult.library.helpers import get_hosts
from catapult.modules.normalizers import normalize_pm2
from catapult.modules.library import get_applications_by_type, get_mirroring_applications, get_balancing_applications
from catapult.modules.balancer import balanced_by_host
from catapult.deploy.constants import SERVER_WEB, SERVER_BOT, HOST_ALL
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
        path = '{}/pm2/check.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'storage': self.storage.get,
            'paths': self.paths.get,
        })

        return generated

    def render_install(self):
        path = '{}/pm2/install.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'release_path': self.paths.get('remote.release'),
            'user': self.storage.get('config.deploy.user'),
            'service_name': 'catapult-{}'.format(self.storage.get('release.service')),
            'storage': self.storage.get,
            'paths': self.paths.get,
        })

        return generated

    def configure(self, config):
        config = normalize_pm2(self.storage.get('release.service'), config)

        pm2 = get_pm2(
            config,
            self.storage,
            self.logger
        )

        configs = {}
        for host in pm2:
            self.storage.start_host(host)

            generated = generate_apps(
                pm2[host],
                self.storage,
                self.paths
            )

            configs[host] = get_json(generated)

            self.storage.finish_host()

        return configs


def get_pm2(applications, storage, logger):
    pm2 = {}

    if storage.is_cluster_mode():
        hosts = storage.get_hosts(HOST_ALL)

        for host in hosts:
            pm2[host] = []

            for application in applications:
                pm2[host].append(application)

        return pm2

    web_servers = storage.get_servers(SERVER_WEB)
    bot_servers = storage.get_servers(SERVER_BOT)

    if web_servers:
        logger.info('configuring pm2 process file for web hosts: {}'.format(
            ', '.join(get_hosts(web_servers)))
        )

    if bot_servers:
        logger.info('configuring pm2 process file for bot hosts: {}'.format(
            ', '.join(get_hosts(web_servers)))
        )

    web_applications = get_applications_by_type(applications, SERVER_WEB)
    bot_applications = get_applications_by_type(applications, SERVER_BOT)

    balancing_applications = get_balancing_applications(bot_applications)
    mirroring_applications = get_mirroring_applications(bot_applications)

    balanced = balanced_by_host(balancing_applications, bot_servers)

    # compose applications by hosts
    for server in bot_servers:
        if server['host'] not in pm2:
            pm2[server['host']] = []

        for application in mirroring_applications:
            pm2[server['host']].append(application)

        for application in balanced[server['host']]:
            pm2[server['host']].append(application)

    # compose applications by hosts
    for server in web_servers:
        if server['host'] not in pm2:
            pm2[server['host']] = []

        for application in web_applications:
            pm2[server['host']].append(application)

    return pm2


def generate_apps(applications, storage, paths):
    apps = []

    for application in applications:
        command = render_string(application['command'], {
            'release_path': paths.get('remote.code'),
            'storage': storage.get,
            'paths': paths.get,
        })

        generated = {
            'name': application['name'],
            'script': command,
            'instances': application['instances'],
            'exec_mode': application['mode'],
            'cwd': paths.get('remote.code')
        }

        apps.append(generated)

    return apps


def get_json(applications):
    json = {
        'apps': applications
    }

    return dumps(json)
