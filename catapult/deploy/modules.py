from os.path import exists
from os import makedirs, chmod
from importlib import import_module
from catapult.library.exceptions import ModuleException
from catapult.library.renders import render_path
from catapult.library.helpers import normalize_linked_paths
from catapult.deploy.constants import REGISTER_INSTALL, REGISTER_CHECK
from catapult.deploy.constants import REGISTER_WEB, REGISTER_BOT, REGISTER_WEB_AND_BOT


class Modules:
    def __init__(self, storage, paths, logger):
        self.storage = storage
        self.paths = paths
        self.logger = logger

        self.modules = {}
        self.registers = {}

        modules = {}
        if storage.get('place.modules'):
            modules = storage.get('place.modules')

        for module_name, module_config in modules.items():
            self.logger.info('instantiate module "{}"'.format(module_name))

            if module_config is None:
                self.logger.info('service config for module "{}" is empty'.format(module_name))

                module_config = {}

            path = '{}/{}/module.py'.format(
                paths.get('catapult.modules'),
                module_name
            )

            if not exists(path):
                raise ModuleException('Module "{}" does not found'.format(module_name))

            imported_module = import_module('catapult.modules.{}.module'.format(module_name))

            instance = imported_module.Module(
                module_config,
                self.storage,
                self.paths,
                self.register,
                self.logger
            )

            self.modules[module_name] = instance

    def register(self, stage, host_type, bash_code):
        if stage not in (REGISTER_INSTALL, REGISTER_CHECK):
            raise ModuleException('Stage type "{}" is not defined'.format(stage))

        if host_type not in (REGISTER_BOT, REGISTER_WEB, REGISTER_WEB_AND_BOT):
            raise ModuleException('Hosts type "{}" is not defined'.format(host_type))

        if stage not in self.registers:
            self.registers[stage] = {}

        if host_type not in self.registers[stage]:
            self.registers[stage][host_type] = []

        self.registers[stage][host_type].append(bash_code)

    def configure(self, deploy_yaml):
        for module_name, module_instance in self.modules.items():
            self.logger.info('configure deploy.yml section "{}"'.format(module_name))

            if module_name not in deploy_yaml:
                self.logger.warning('section "{}" does not exist in deploy.yml, skipped'.format(module_name))

                continue

            config = deploy_yaml[module_name]

            config_by_host = module_instance.configure(config)

            if not type(config_by_host) is dict:
                self.logger.info('module "{}" does not return configure data, skipped'.format(module_name))
                continue

            for host, generated in config_by_host.items():
                folder = '{}/{}'.format(self.paths.get('local.configs'), host)

                if not exists(folder):
                    makedirs(folder)

                with open('{}/{}'.format(folder, module_name), 'w') as open_file:
                    open_file.write(generated)

        self.logger.info('configuring install scripts')
        configure_install(self.storage, self.paths, self.registers)

        self.logger.info('configuring check scripts')
        configure_check(self.storage, self.paths, self.registers)


def configure_install(storage, paths, registers):
    web_items = ''
    if REGISTER_INSTALL in registers and REGISTER_WEB in registers[REGISTER_INSTALL]:
        web_items = '\n'.join(registers[REGISTER_INSTALL][REGISTER_WEB])

    bot_items = ''
    if REGISTER_INSTALL in registers and REGISTER_BOT in registers[REGISTER_INSTALL]:
        bot_items = '\n'.join(registers[REGISTER_INSTALL][REGISTER_BOT])

    web_and_bot_items = ''
    if REGISTER_INSTALL in registers and REGISTER_WEB_AND_BOT in registers[REGISTER_INSTALL]:
        web_and_bot_items = '\n'.join(registers[REGISTER_INSTALL][REGISTER_WEB_AND_BOT])

    linked_paths = normalize_linked_paths(storage.get('place.linked'))

    path = '{}/core/install.j2'.format(
        paths.get('catapult.templates'),
    )

    generated = render_path(path, {
        'release_path': paths.get('remote.release'),
        'release_name': storage.get('release.name'),
        'user': storage.get('config.deploy.user'),
        'service_name': storage.get('release.service'),
        'file_name': 'catapult-{}'.format(storage.get('release.service')),
        'deploy_path': storage.get('config.deploy.deploy_path'),
        'linked_paths': linked_paths,
        'web_items': web_items,
        'bot_items': bot_items,
        'web_and_bot_items': web_and_bot_items,
    })

    file = '{}/install.sh'.format(paths.get('local.release'))
    with open(file, 'w') as open_file:
        open_file.write(generated)

    chmod(file, 0o0766)


def configure_check(storage, paths, registers):
    web_items = ''
    if REGISTER_CHECK in registers and REGISTER_WEB in registers[REGISTER_CHECK]:
        web_items = '\n'.join(registers[REGISTER_CHECK][REGISTER_WEB])

    bot_items = ''
    if REGISTER_CHECK in registers and REGISTER_BOT in registers[REGISTER_CHECK]:
        bot_items = '\n'.join(registers[REGISTER_CHECK][REGISTER_BOT])

    web_and_bot_items = ''
    if REGISTER_CHECK in registers and REGISTER_WEB_AND_BOT in registers[REGISTER_CHECK]:
        web_and_bot_items = '\n'.join(registers[REGISTER_CHECK][REGISTER_WEB_AND_BOT])

    path = '{}/core/check.j2'.format(
        paths.get('catapult.templates'),
    )

    generated = render_path(path, {
        'user': storage.get('config.deploy.user'),
        'service_name': storage.get('release.service'),
        'deploy_path': storage.get('config.deploy.deploy_path'),
        'web_items': web_items,
        'bot_items': bot_items,
        'web_and_bot_items': web_and_bot_items,
    })

    file = '{}/check.sh'.format(paths.get('local.release'))
    with open(file, 'w') as open_file:
        open_file.write(generated)

    chmod(file, 0o0766)
