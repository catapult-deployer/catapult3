import time
from os.path import normpath, join
from catapult.library.exceptions import ConfigParserException
from catapult.library.helpers import generate_release_name, get_messages
from catapult.deploy.constants import CLOUD, CLUSTER
from catapult.deploy.constants import SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN


def transform_arguments_parameters(arguments):
    parameters = {}

    for pare in arguments:
        stack = pare.split(':')

        if len(stack) != 2:
            raise ConfigParserException('Parameter must be specify as key:value string')

        parameters[stack[0]] = stack[1]

    return parameters


def saturate_request(request):
    release_name = generate_release_name(request['service'], request['branch'])

    wrapper = {
        'name': release_name,
        'time_start': int(time.time()),
    }

    return {
        **request,
        **wrapper,
    }


def from_args_to_request(arguments):
    parameters = transform_arguments_parameters(arguments.parameter)

    return {
        'branch': arguments.branch,
        'commands': arguments.command,
        'force': arguments.force,
        'parameters': parameters,
        'place': arguments.place,
        'service': arguments.service,
    }


def transform_server_request(request):
    commands = []
    if 'commands' in request:
        commands = request['commands']

    parameters = {}
    if 'parameters' in request:
        parameters = request['parameters']

    force = False
    if 'force' in request:
        force = request['force']

    branch = ''
    if 'branch' in request:
        branch = request['branch']

    service = ''
    if 'service' in request:
        service = request['service']

    place = ''
    if 'place' in request:
        place = request['place']

    return {
        'branch': branch.strip(),
        'commands': commands,
        'force': force,
        'parameters': parameters,
        'place': place.strip(),
        'service': service.strip(),
    }


def transform_service(service, config):
    parameters = {}
    if 'parameters' in service:
        parameters = service['parameters']

    recipes = []
    if 'recipes' in service:
        recipes = service['recipes']

    for place in service['places']:
        # set repo
        service['places'][place]['repo'] = service['repo']

        # set registry
        service['places'][place]['registry'] = ''
        if 'registry' in service:
            service['places'][place]['registry'] = service['registry']

        # set linked paths
        service['places'][place]['linked'] = []
        if 'linked' in service:
            service['places'][place]['linked'] = service['linked']

        # transform recipes
        if 'recipes' not in service['places'][place]:
            service['places'][place]['recipes'] = recipes
        else:
            service['places'][place]['recipes'] = list(set(recipes + service['places'][place]['recipes']))

        # transform parameters
        if 'parameters' not in service['places'][place]:
            service['places'][place]['parameters'] = parameters
        else:
            service['places'][place]['parameters'] = {
                **parameters,
                **service['places'][place]['parameters'],
            }

        # transform modules
        if 'modules' not in service['places'][place]:
            service['places'][place]['modules'] = {}

        if service['places'][place]['modules'] is None:
            service['places'][place]['modules'] = {}

        if 'modules' in service['places'][place]:
            for module_name, module_config in service['places'][place]['modules'].items():
                if module_config is None:
                    service['places'][place]['modules'][module_name] = {}

        # transform weight for bot servers of cloud
        if CLOUD in service['places'][place] and SERVER_BOT in service['places'][place][CLOUD]:
            for server in service['places'][place][CLOUD][SERVER_BOT]:
                if 'weight' not in server:
                    server['weight'] = 1

        # transform weight for servers in cluster
        if CLUSTER in service['places'][place]:
            for server in service['places'][place][CLUSTER]:
                if 'weight' not in server:
                    server['weight'] = 1

        # transform parameters for CLOUD
        if CLOUD in service['places'][place]:
            for host_type in (SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN):
                if host_type in service['places'][place][CLOUD]:
                    for server in service['places'][place][CLOUD][host_type]:
                        if 'parameters' not in server:
                            server['parameters'] = {}

        # transform parameters for CLUSTER
        if CLUSTER in service['places'][place]:
            for server in service['places'][place][CLUSTER]:
                if 'parameters' not in server:
                    server['parameters'] = {}

        # transform notifications
        if 'notifications' in config:
            if 'notifications' not in service['places'][place]:
                service['places'][place]['notifications'] = {}

            # set base parameters for transport
            for transport in config['notifications']:
                if transport not in service['places'][place]['notifications']:
                    continue

                # set token for all transports
                service['places'][place]['notifications'][transport]['token'] = \
                    config['notifications'][transport]['token']

                # patch messages templates for transports
                messages = get_messages(config['notifications'][transport])

                if 'messages' not in service['places'][place]['notifications'][transport]:
                    service['places'][place]['notifications'][transport]['messages'] = messages

                if 'success' not in service['places'][place]['notifications'][transport]['messages']:
                    service['places'][place]['notifications'][transport]['messages']['success'] = \
                        messages['success']

                if 'fail' not in service['places'][place]['notifications'][transport]['messages']:
                    service['places'][place]['notifications'][transport]['messages']['fail'] = \
                        messages['fail']

    return service


def transform_config(project_path, config):
    # generate absolute path to ssh.key_file
    ssh_key_file = normpath(config['deploy']['ssh']['key_file'])
    ssh_key_file = join(project_path, ssh_key_file)
    config['deploy']['ssh']['key_file'] = ssh_key_file

    # generate absolute path to git.key_file
    git_key_file = normpath(config['deploy']['git']['key_file'])
    git_key_file = join(project_path, git_key_file)
    config['deploy']['git']['key_file'] = git_key_file

    if 'registry' in config:
        if 'base_url' not in config['registry']:
            config['registry']['base_url'] = 'unix://var/run/docker.sock'

    return config
