import os
from catapult.library.helpers import parse_yaml
from catapult.library.exceptions import ConfigParserException
from catapult.library.validators import validate_service, validate_config
from catapult.library.transformers import transform_service, transform_config


def parse_services(project_path, main_config):
    services_path = os.path.join(project_path, 'services')

    if not os.path.isdir(services_path):
        raise ConfigParserException('You must provide service folder in path {}'.format(project_path))

    services = {}

    for service in os.listdir(services_path):
        service_path = os.path.join(services_path, service)

        if not os.path.isdir(service_path):
            continue

        config_path = os.path.join(service_path, 'config.yml')

        if not os.path.isfile(config_path):
            raise ConfigParserException('You must specify config.yml file for service {}'.format(service))

        config = parse_yaml(config_path)

        validate_service(service, config)

        services[service] = transform_service(config, main_config)

    return services


def parse_config(project_path):
    config_path = os.path.join(project_path, 'config.yml')

    if not os.path.isfile(config_path):
        raise ConfigParserException('You must provide config.yml file in path {}'.format(project_path))

    config = parse_yaml(config_path)

    validate_config(config)

    transform_config(project_path, config)

    return config

