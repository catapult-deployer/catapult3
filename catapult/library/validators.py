import re
from catapult.library.helpers import parse_nested_parameters
from catapult.library.exceptions import InvalidRequestException, ConfigParserException
from catapult.deploy.constants import SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN
from catapult.deploy.constants import TRANSPORT_TELEGRAM, TRANSPORT_SLACK, TRANSPORT_PUSHOVER
from catapult.deploy.constants import CLOUD, CLUSTER


def validate_request(request, services):
    if not request['service']:
        raise InvalidRequestException('Service name must be specified')

    if not request['branch']:
        raise InvalidRequestException('Branch name must be specified')

    if not request['place']:
        raise InvalidRequestException('Place name must be specified')

    for command in request['commands']:
        if not isinstance(command, str):
            raise InvalidRequestException('All commands must be string')

    if request['service'] not in services:
        raise InvalidRequestException('Service with name "{}" does not found'.format(request['service']))

    if request['place'] not in services[request['service']]['places']:
        raise InvalidRequestException(
            'Place "{}" for service "{}" does not found'.format(
                request['place'],
                request['service']
            )
        )


def validate_config(config):
    if 'deploy' not in config or not config['deploy']:
        raise ConfigParserException('You must provide section "deploy" in config.yml file')

    if 'user' not in config['deploy']:
        raise ConfigParserException('You must provide "user" in section "deploy" of config.yml file')

    if 'deploy_path' not in config['deploy']:
        raise ConfigParserException('You must provide "deploy_path" in section "deploy" of config.yml file')

    if 'keep_releases' not in config['deploy']:
        raise ConfigParserException('You must provide "keep_releases" in section "deploy" of config.yml file')

    if 'ssh' not in config['deploy'] or not config['deploy']['ssh']:
        raise ConfigParserException('You must provide "ssh" section in section "deploy" of config.yml file')

    if 'user' not in config['deploy']['ssh']:
        raise ConfigParserException('You must provide "user" in section "ssh" in section "deploy" of config.yml file')

    if 'key_file' not in config['deploy']['ssh']:
        raise ConfigParserException(
            'You must provide "key_file" in section "ssh" in section "deploy" of config.yml file'
        )

    if 'git' not in config['deploy'] or not config['deploy']['git']:
        raise ConfigParserException('You must provide "git" section in section "deploy" of config.yml file')

    if 'key_file' not in config['deploy']['git']:
        raise ConfigParserException(
            'You must provide "key_file" in section "git" in section "deploy" of config.yml file'
        )

    if 'server' not in config or not config['server']:
        raise ConfigParserException('You must provide section "server" in config.yml file')

    if 'token' not in config['server']:
        raise ConfigParserException('You must provide "token" in section "server" of config.yml file')

    if 'workers' not in config['server']:
        raise ConfigParserException('You must provide "workers" in section "server" of config.yml file')

    if 'host' not in config['server']:
        raise ConfigParserException('You must provide "host" in section "server" of config.yml file')

    if 'port' not in config['server']:
        raise ConfigParserException('You must provide "port" in section "server" of config.yml file')

    if 'registry' in config:
        if 'server' not in config['registry']:
            raise ConfigParserException('You must provide "server" in section "registry" of config.yml file')

        if 'username' not in config['registry']:
            raise ConfigParserException('You must provide "username" in section "registry" of config.yml file')

        if 'password' not in config['registry']:
            raise ConfigParserException('You must provide "password" in section "registry" of config.yml file')

    if 'notifications' in config:
        for transport in config['notifications']:
            if 'token' not in config['notifications'][transport]:
                raise ConfigParserException(
                    'You must specify "token" field for notification transport "{}"'.format(transport)
                )

            if 'messages' in config['notifications'][transport]:
                if not isinstance(config['notifications'][transport]['messages'], dict):
                    raise ConfigParserException(
                        'Field "messages" for transport "{}" must be a dict in config.yml file'.format(transport)
                    )


def validate_service(service_name, config):
    pattern_validate = '^[a-z0-9-]+$'
    regular_validate = re.compile(pattern_validate)

    if not regular_validate.match(service_name):
        raise ConfigParserException(
            'Name of service "{}" must match to pattern "{}"'.format(
                service_name,
                pattern_validate
            )
        )

    if 'repo' not in config or not config['repo'] or not isinstance(config['repo'], str):
        raise ConfigParserException('You must specify section "repo" in config.yml of service "{}"'.format(service_name))

    if 'places' not in config or not config['places']:
        raise ConfigParserException('You must specify section "places" in config.yml of service "{}"'.format(service_name))

    if 'linked' in config and not isinstance(config['linked'], list):
        raise ConfigParserException(
            'Section "linked" for service "{}" must be a list'.format(service_name)
        )

    if 'parameters' in config and not isinstance(config['parameters'], dict):
        raise ConfigParserException(
            'Section "parameters" for service "{}" must be a dict'.format(service_name)
        )

    for place_name in config['places']:
        place = config['places'][place_name]

        if 'linked' in place:
            raise ConfigParserException(
                'You must remove section "linked" for place "{}" of service "{}"'.format(place_name, service_name)
            )

        if CLUSTER not in place and CLOUD not in place:
            raise ConfigParserException(
                'You must specify "{}" or "{}" section for place "{}" of service "{}"'.format(
                    CLUSTER,
                    CLOUD,
                    place_name,
                    service_name
                )
            )

        if CLUSTER in place and CLOUD in place:
            raise ConfigParserException(
                'You must specify "{}" or "{}" section for place "{}" of service "{}"'.format(
                    CLUSTER,
                    CLOUD,
                    place_name,
                    service_name
                )
            )

        if CLOUD in place:
            if not isinstance(place[CLOUD], dict):
                raise ConfigParserException(
                    'Section "cloud" for place "{}" of service "{}" must be a dict of'
                    ' "{}", "{}" and "{}" servers'.format(
                        SERVER_WEB,
                        SERVER_BOT,
                        SERVER_MAINTAIN,
                        place_name,
                        service_name
                    )
                )

            if SERVER_WEB not in place[CLOUD] and SERVER_BOT not in place[CLOUD]:
                raise ConfigParserException(
                    'You must specify "{}" or "{}" section for place "{}" of service "{}"'.format(
                        SERVER_WEB,
                        SERVER_BOT,
                        place_name,
                        service_name
                    )
                )

            if SERVER_WEB in place[CLOUD] and not isinstance(place[CLOUD][SERVER_WEB], list):
                raise ConfigParserException(
                    'Section "{}" for place "{}" of service "{}" must be list of servers'.format(
                        SERVER_WEB,
                        place_name,
                        service_name
                    )
                )

            if SERVER_BOT in place[CLOUD] and not isinstance(place[CLOUD][SERVER_BOT], list):
                raise ConfigParserException(
                    'Section "{}" for place "{}" of service "{}" must be list of servers'.format(
                        SERVER_BOT,
                        place_name,
                        service_name
                    )
                )

            if SERVER_MAINTAIN in place[CLOUD] and not isinstance(place[CLOUD][SERVER_MAINTAIN], list):
                raise ConfigParserException(
                    'Section "{}" for place "{}" of service "{}" must be a list of servers'.format(
                        SERVER_MAINTAIN,
                        place_name,
                        service_name,
                    )
                )

            # check unique servers
            servers = []
            for host_type in (SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN):
                if host_type in place[CLOUD]:
                    for item in place[CLOUD][host_type]:
                        if 'host' not in item:
                            raise ConfigParserException(
                                'You must specify "{}" host for place "{}" of service "{}"'.format(
                                    host_type,
                                    place_name,
                                    service_name,
                                )
                            )

                        servers.append(item['host'])
            if sorted(list(set(servers))) != sorted(servers):
                raise ConfigParserException(
                    'All hosts for for place "{}" of service "{}" must be unique'.format(
                        place_name,
                        service_name,
                    )
                )

            # check weight for servers
            if SERVER_BOT in place[CLOUD]:
                is_weight_set = False
                for server in place[CLOUD][SERVER_BOT]:
                    if 'weight' in server:
                        if not isinstance(server['weight'], int):
                            raise ConfigParserException(
                                '"weight" for place "{}" of service "{}" must be integer'.format(
                                    place_name,
                                    service_name,
                                )
                            )

                        is_weight_set = True

                    if 'weight' not in server and is_weight_set is True:
                        raise ConfigParserException(
                            'You must specify "weight" for host "{}" in place "{}"'.format(
                                server['host'],
                                place_name,
                            )
                        )

                    if is_weight_set is True and (server['weight'] > 3 or server['weight'] <= 0):
                        raise ConfigParserException(
                            '"weight" for host "{}" in place "{}" must be between 1 and 3'.format(
                                server['host'],
                                place_name,
                            )
                        )

            # check parameters
            is_set_checked = False
            checked_parameters = []
            checked_host = ''
            for host_type in (SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN):
                if host_type in place[CLOUD]:
                    for server in place[CLOUD][host_type]:
                        if 'parameters' in server and not isinstance(server['parameters'], dict):
                            raise ConfigParserException(
                                'Section "parameters" for service "{}" and place "{}" '
                                'and servers type "{}" and host "{}" must be a dict'.format(
                                    service_name,
                                    place_name,
                                    host_type,
                                    server['host']
                                )
                            )

                        parameters = {}
                        if 'parameters' in server:
                            parameters = server['parameters']

                        parameters = parse_nested_parameters(parameters)

                        if not is_set_checked:
                            is_set_checked = True
                            checked_parameters = parameters
                            checked_host = server['host']

                            continue

                        more_diff = list(set(checked_parameters) - set(parameters))
                        less_diff = list(set(parameters) - set(checked_parameters))

                        if more_diff:
                            raise ConfigParserException(
                                'You must specify parameters "{}" for service "{}" and place "{}" '
                                'and servers type "{}" and host "{}"'.format(
                                    ', '.join(more_diff),
                                    service_name,
                                    place_name,
                                    host_type,
                                    server['host']
                                )
                            )

                        if less_diff:
                            raise ConfigParserException(
                                'You must specify parameters "{}" for service "{}" and place "{}" '
                                'and servers type "{}" and host "{}"'.format(
                                    ', '.join(less_diff),
                                    service_name,
                                    place_name,
                                    host_type,
                                    checked_host
                                )
                            )

        if CLUSTER in place:
            if not isinstance(place[CLUSTER], list):
                raise ConfigParserException(
                    'Section "cluster" for place "{}" of service "{}" must be a list of servers'.format(
                        place_name,
                        service_name
                    )
                )

            # check unique servers
            servers = []
            for server in place[CLUSTER]:
                if 'host' not in server:
                    raise ConfigParserException(
                        'You must specify host for place "{}" of service "{}"'.format(
                            place_name,
                            service_name,
                        )
                    )

                servers.append(server['host'])
            if sorted(list(set(servers))) != sorted(servers):
                raise ConfigParserException(
                    'All hosts for for place "{}" of service "{}" must be unique'.format(
                        place_name,
                        service_name,
                    )
                )

            # check weight for servers
            is_weight_set = False
            for server in place[CLUSTER]:
                if 'weight' in server:
                    if not isinstance(server['weight'], int):
                        raise ConfigParserException(
                            '"weight" for place "{}" of service "{}" must be integer'.format(
                                place_name,
                                service_name,
                            )
                        )

                    is_weight_set = True

                if 'weight' not in server and is_weight_set is True:
                    raise ConfigParserException(
                        'You must specify "weight" for host "{}" in place "{}"'.format(
                            server['host'],
                            place_name,
                        )
                    )

                if is_weight_set is True and (server['weight'] > 3 or server['weight'] <= 0):
                    raise ConfigParserException(
                        '"weight" for host "{}" in place "{}" must be between 1 and 3'.format(
                            server['host'],
                            place_name,
                        )
                    )

            # check parameters
            is_set_checked = False
            checked_parameters = []
            checked_host = ''
            for server in place[CLUSTER]:
                if 'parameters' in server and not isinstance(server['parameters'], dict):
                    raise ConfigParserException(
                        'Section "parameters" for service "{}" and place "{}" and host "{}" must be a dict'.format(
                            service_name,
                            place_name,
                            server['host']
                        )
                    )

                parameters = {}
                if 'parameters' in server:
                    parameters = server['parameters']

                parameters = parse_nested_parameters(parameters)

                if not is_set_checked:
                    is_set_checked = True
                    checked_parameters = parameters
                    checked_host = server['host']

                    continue

                more_diff = list(set(checked_parameters) - set(parameters))
                less_diff = list(set(parameters) - set(checked_parameters))

                if more_diff:
                    raise ConfigParserException(
                        'You must specify parameters "{}" for service "{}" and place "{}" '
                        'and host "{}"'.format(
                            ', '.join(more_diff),
                            service_name,
                            place_name,
                            server['host']
                        )
                    )

                if less_diff:
                    raise ConfigParserException(
                        'You must specify parameters "{}" for service "{}" and place "{}" '
                        'and host "{}"'.format(
                            ', '.join(less_diff),
                            service_name,
                            place_name,
                            checked_host
                        )
                    )

        if 'recipes' in place and not isinstance(place['recipes'], list):
            raise ConfigParserException(
                'Section "recipes" for place "{}" of service "{}" must be a list'.format(place_name, service_name)
            )

        if 'parameters' in place and not isinstance(place['parameters'], dict):
            raise ConfigParserException(
                'Section "parameters" for place "{}" of service "{}" must be a dict'.format(place_name, service_name)
            )

        if 'notifications' in place:
            if not isinstance(place['notifications'], dict):
                raise ConfigParserException(
                    'Section "notifications" for place "{}" of service "{}" must be a dict'.format(place_name, service_name)
                )

            for transport in place['notifications']:
                if not isinstance(place['notifications'][transport], dict):
                    raise ConfigParserException(
                        'Section "{}" for place "{}" of service "{}" must be a dict'.format(
                            transport,
                            place_name,
                            service_name
                        )
                    )

                if transport == TRANSPORT_TELEGRAM:
                    if 'chat_id' not in place['notifications'][transport]:
                        raise ConfigParserException(
                            'You must specify "chat_id" field for transport "{}" for place "{}" of service "{}"'.format(
                                transport,
                                place_name,
                                service_name,
                            )
                        )

                    if not isinstance(place['notifications'][transport]['chat_id'], str):
                        raise ConfigParserException(
                            'Field "chat_id" for transport "{}" for place "{}" of service "{}" must be a string'.format(
                                transport,
                                place_name,
                                service_name
                            )
                        )

                if transport == TRANSPORT_SLACK:
                    if 'channel' not in place['notifications'][transport]:
                        raise ConfigParserException(
                            'You must specify "channel" field for transport "{}" for place "{}" of service "{}"'.format(
                                transport,
                                place_name,
                                service_name,
                            )
                        )

                    if not isinstance(place['notifications'][transport]['channel'], str):
                        raise ConfigParserException(
                            'Field "channel" for transport "{}" for place "{}" of service "{}" must be a string'.format(
                                transport,
                                place_name,
                                service_name
                            )
                        )

                if transport == TRANSPORT_PUSHOVER:
                    if 'clients' not in place['notifications'][transport]:
                        raise ConfigParserException(
                            'You must specify "clients" field for transport "{}" for place "{}" of service "{}"'.format(
                                transport,
                                place_name,
                                service_name,
                            )
                        )

                    if not isinstance(place['notifications'][transport]['clients'], list):
                        raise ConfigParserException(
                            'Field "clients" for transport "{}" must be a list for place "{}" of service "{}"'.format(
                                TRANSPORT_PUSHOVER,
                                place_name,
                                service_name,
                            )
                        )
