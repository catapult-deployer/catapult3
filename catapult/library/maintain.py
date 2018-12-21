from catapult.deploy.constants import HOST_MAINTAIN
from catapult.library.renders import render_string


def execute_maintain(storage, paths, ssh, commands, logger, recipe_name=None):
    hosts = storage.get_hosts(HOST_MAINTAIN)

    path_commands = wrap_commands_with_path(storage, paths, commands)

    # list of hosts is empty
    if not hosts and path_commands:
        logger.warning('list of maintain servers is empty. Following commands will be skipped:', recipe_name)

        for command in path_commands:
            if recipe_name:
                logger.warning(command, recipe_name)
            else:
                logger.warning(command)

    execute_commands_on_maintain(
        hosts,
        ssh,
        logger,
        path_commands,
        recipe_name
    )


def execute_commands_on_maintain(hosts, ssh, logger, commands, recipe_name=None):
    hosts_iteration = iter(hosts)
    host = next(hosts_iteration)

    for command in commands:
        if recipe_name:
            logger.info('execute recipe command "{}" on host "{}"'.format(command, host), recipe_name)
        else:
            logger.info('execute command "{}"'.format(command), host)

        ssh.execute_on_host(host, command)

        try:
            host = next(hosts_iteration)
        except StopIteration:
            hosts_iteration = iter(hosts)
            host = next(hosts_iteration)


def wrap_commands_with_path(storage, paths, commands):
    path_commands = []

    for command in commands:
        command = 'cd {} && {}'.format(
            paths.get('remote.code'),
            command
        )

        command = render_string(command, {
            'storage': storage.get,
            'paths': paths.get,
        })

        path_commands.append(command)

    return path_commands
