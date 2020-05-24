import os
import re
import yaml
import shutil
import logging
import random
from datetime import datetime
from catapult.library.exceptions import ConfigParserException, InvalidParameterException
from catapult.deploy.constants import CLOUD, CLUSTER
from catapult.deploy.constants import SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN


def parse_yaml(path):
    if not os.path.isfile(path):
        raise ConfigParserException('Yaml file by path "{}" does not found'.format(path))

    with open(path) as stream:
        try:
            return yaml.load(stream, Loader=yaml.Loader)
        except Exception as error:
            raise ConfigParserException(
                'An error occurred with parsing yaml file by path "{}":\n\n{}'.format(
                    path,
                    indented_error(error)
                )
            )


def indented_error(error):
    indent = '>>> '
    splitted = str(error).split('\n')

    return indent + ('\n' + indent).join(splitted)


def generate_release_name(service, branch):
    if len(branch) > 25:
        branch = branch[0:25]

    time_start = str('{:%y%m%d%H%M%S}'.format(datetime.now()))

    number = int(random.uniform(0, 20))
    if number <= 9:
        number = '0' + str(number)
    number = str(number)

    cleaned_branch = re.sub('[^A-Za-z0-9]+', '_', branch)
    cleaned_service = re.sub('[^A-Za-z0-9]+', '_', service)

    release_name = '{}{}_{}_{}'.format(
        time_start,
        number,
        cleaned_service,
        cleaned_branch
    )

    return release_name.lower()


def get_nested(path, dictionary):
    splitted = path.split('.')

    for section in splitted:
        if section not in dictionary:
            raise InvalidParameterException(
                'Section with name "{}" does not found in path "{}"'.format(section, path)
            )

        dictionary = dictionary[section]

        if dictionary is None:
            raise InvalidParameterException(
                'Section with name "{}" is empty in path "{}"'.format(section, path)
            )

    return dictionary


def get_place(services, service, place):
    if service not in services:
        raise ConfigParserException('Service "{}" does not found'.format(service))

    if place not in services[service]['places']:
        raise ConfigParserException('Place "{}" does not found in service "{}"'.format(place, service))

    return services[service]['places'][place]


def normalize_linked_paths(paths):
    if paths is None:
        return []

    paths = sorted(paths, key=len, reverse=True)

    normalized = []

    for path in paths:
        normalized.append(path.strip('/'))

    linked_paths = '"{0}"'.format('" "'.join(normalized))

    return linked_paths


def get_hosts(servers):
    hosts = []

    for server in servers:
        hosts.append(server['host'])

    return hosts


def get_messages(main_transport_config):
    message_success = 'Branch "{{ branch }}" of service "{{ service }}" ' \
                      'successfully deployed for place "{{ place }}" with {{ time }}s'
    message_fail = 'Error with deploy branch "{{ branch }}" of service "{{ service }}" for place "{{ place }}"'

    if 'messages' not in main_transport_config:
        return {
            'success': message_success,
            'fail': message_fail,
        }

    if 'success' in main_transport_config['messages']:
        message_success = main_transport_config['messages']['success']

    if 'fail' in main_transport_config['messages']:
        message_fail = main_transport_config['messages']['fail']

    return {
        'success': message_success,
        'fail': message_fail,
    }


def remove_releases_folder(project_path):
    releases_path = os.path.join(project_path, 'releases')

    if os.path.exists(releases_path):
        logging.info('deleting folder {}'.format(releases_path))

        shutil.rmtree(releases_path)


def start_logging(project_path):
    logging_path = os.path.join(project_path, 'server.log')

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)-5.5s] %(message)s",
        filename=logging_path,
    )

    logging.info('-' * 100)


def parse_nested_parameters(parameters, prefix=''):
    reducer = []

    for key, value in parameters.items():
        prefixed = prefix
        if prefix:
            prefixed = '{}.'.format(prefix)

        name = '{}{}'.format(prefixed, key)

        if isinstance(value, dict):
            reducer += parse_nested_parameters(value, name)
        else:
            reducer.append(name)

    return reducer


def get_parameters_by_host(place):
    parameters = {}

    if CLOUD in place:
        for host_type in (SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN):
            if host_type in place[CLOUD]:
                for server in place[CLOUD][host_type]:
                    parameters[server['host']] = server['parameters']

    if CLUSTER in place:
        for server in place[CLUSTER]:
            parameters[server['host']] = server['parameters']

    return parameters
