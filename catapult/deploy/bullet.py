from catapult.library.exceptions import RecipeException
from catapult.deploy.constants import HOST_WEB, HOST_BOT, HOST_MAINTAIN, HOST_ALL
from catapult.deploy.constants import BULLET_LOCAL, BULLET_MAINTAIN, BULLET_CONSOLE, BULLET_REMOTE


class Bullet:
    def __init__(self):
        self.commands = []

    def local(self, command):
        self.commands.append({
            'type': BULLET_LOCAL,
            'command': command
        })

    def remote(self, types, command, is_sudo=False):
        if type(types) is str:
            types = [types]

        if not isinstance(command, str):
            raise RecipeException('Recipe command "{}" must be a string'.format(command))

        if not isinstance(types, list):
            raise RecipeException('Recipe server types "{}" must be a string or a list'.format(types))

        for host_type in types:
            if host_type not in (HOST_WEB, HOST_BOT, HOST_MAINTAIN, HOST_ALL):
                raise RecipeException(
                    'Recipe server type "{}" is undefined'.format(command, host_type)
                )

        self.commands.append({
            'type': BULLET_REMOTE,
            'is_sudo': True if is_sudo else False,
            'types': types,
            'command': command
        })

    def maintain(self, commands):
        if not isinstance(commands, list):
            raise RecipeException('Commands "{}" for maintain must be a list'.format(commands))

        self.commands.append({
            'type': BULLET_MAINTAIN,
            'commands': commands
        })

    def console(self, message):
        if not isinstance(message, str):
            raise RecipeException('Console message "{}" for recipe must be a string'.format(message))

        self.commands.append({
            'type': BULLET_CONSOLE,
            'message': message
        })

    def get_commands(self):
        return self.commands
