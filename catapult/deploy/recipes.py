import sys
import importlib
import subprocess
import inspect
from os.path import exists
from catapult.library.renders import render_string
from catapult.library.maintain import execute_maintain
from catapult.library.exceptions import RecipeException
from catapult.deploy.bullet import Bullet
from catapult.deploy.constants import STATE_BEFORE, STATE_AFTER
from catapult.deploy.constants import BULLET_LOCAL, BULLET_MAINTAIN, BULLET_CONSOLE, BULLET_REMOTE


class Recipes:
    def __init__(self, storage, paths, ssh, logger):
        self.storage = storage
        self.paths = paths
        self.ssh = ssh
        self.logger = logger

        self.recipes = {}

        recipes = self.storage.get('place.recipes')

        if not recipes:
            return

        sys.path.insert(0, paths.get('local.project_path'))

        for recipe in recipes:
            recipe_path = '{}/{}.py'.format(
                paths.get('local.recipes'),
                recipe
            )

            if not exists(recipe_path):
                raise RecipeException(
                    'Recipe "{}" does not found by path "{}"'.format(
                        recipe,
                        recipe_path
                    )
                )

            imported_module = importlib.import_module('recipes.{}'.format(recipe))

            recipe_arguments = inspect.getfullargspec(imported_module.Recipe.__init__)
            if len(recipe_arguments.args) < 2:
                raise RecipeException(
                    'You must specify second argument of __init__ method of recipe "{}" as Storage object'.format(
                        recipe
                    )
                )

            instance = imported_module.Recipe(
                self.storage,
                self.paths
            )

            self.recipes[recipe] = instance

    def execute(self, state, phase):
        if not self.recipes:
            self.logger.info('recipes list is empty, skipped'.format(phase))

            return

        if state not in (STATE_BEFORE, STATE_AFTER):
            raise RecipeException('Invalid state "{}" for execute recipe'.format(state))

        for recipe_name, recipe_instance in self.recipes.items():
            method_name = '{}_{}'.format(state, phase)

            if method_name not in dir(recipe_instance):
                self.logger.info(
                    'action "{}" phase "{}" for recipe "{}" not exists, skipped'.format(
                        state,
                        phase,
                        recipe_name
                    )
                )

                continue

            bullet = Bullet()

            method_link = getattr(recipe_instance, method_name)
            method_link(bullet)

            commands = bullet.get_commands()

            for command in commands:
                if command['type'] == BULLET_LOCAL:
                    execute_local(
                        self.storage,
                        self.paths,
                        self.logger,
                        recipe_name,
                        command['command']
                    )
                    continue

                if command['type'] == BULLET_REMOTE:
                    execute_remote(
                        self.storage,
                        self.paths,
                        self.ssh,
                        self.logger,
                        recipe_name,
                        command['command'],
                        command['types'],
                        command['is_sudo']
                    )

                    continue

                if command['type'] == BULLET_MAINTAIN:
                    execute_maintain(
                        self.storage,
                        self.paths,
                        self.ssh,
                        command['commands'],
                        self.logger,
                        recipe_name,
                    )

                    continue

                if command['type'] == BULLET_CONSOLE:
                    self.logger.info(command['message'], recipe_name)

                    continue


def execute_local(storage, paths, logger, recipe_name, command):
    command = render_string(command, {
        'storage': storage.get,
        'paths': paths.get,
    })

    command = 'cd {} && {}'.format(
        paths.get('local.code'),
        command
    )

    # show log message
    logger.info('execute local command "{}"'.format(command), recipe_name)

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    for line in iter(process.stdout.readline, ''):
        logger.success(line.strip('\n'), recipe_name)

    for line in iter(process.stderr.readline, ''):
        logger.error(line.strip('\n'), recipe_name)

    process.stdout.close()
    process.stderr.close()

    exit_code = process.wait()
    if exit_code != 0:
        raise RecipeException('Execution error with command "{}"'.format(command))


def execute_remote(storage, paths, ssh, logger, recipe_name, command, types, is_sudo):
    if is_sudo:
        command = 'sudo {}'.format(command)

    command = 'cd {} && {}'.format(
        paths.get('remote.code'),
        command
    )

    command = render_string(command, {
        'storage': storage.get,
        'paths': paths.get,
    })

    # show log message
    logger.info('execute remote command "{}"'.format(command), recipe_name)

    for host_type in types:
        hosts = storage.get_hosts(host_type)

        for host in hosts:
            ssh.execute_on_host(host, command)
