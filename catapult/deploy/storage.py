from catapult.library.helpers import get_nested
from catapult.library.exceptions import InvalidParameterException
from catapult.library.helpers import get_hosts, get_parameters_by_host
from catapult.deploy.constants import SERVER_BOT, SERVER_MAINTAIN, SERVER_WEB
from catapult.deploy.constants import HOST_ALL, HOST_WEB, HOST_BOT, HOST_MAINTAIN
from catapult.deploy.constants import CLOUD, CLUSTER

PARAMETERS_PREFIX = 'parameters.'


class Storage:
    def __init__(self, config, place, request):
        parameters = {
            **place['parameters'],
            **request['parameters'],
        }

        self.host_parameters = get_parameters_by_host(place)

        storage = {
            'release': request,
            'parameters': parameters,
            'place': place,
            'config': config,
        }

        self.storage = storage
        self.host = None

    def start_host(self, host):
        self.host = host

    def finish_host(self):
        self.host = None

    def get(self, path, default=None):
        # try to get host parameters
        if path.startswith(PARAMETERS_PREFIX) and self.host:
            try:
                return get_nested(
                    path[len(PARAMETERS_PREFIX):],
                    self.host_parameters[self.host]
                )
            except InvalidParameterException:
                pass

        """
            config.*
            place.*
            parameters.*

            release.name
            release.place
            release.branch
            release.service
            release.force
            release.commands
            release.parameters
            release.time_start
        """
        try:
            return get_nested(path, self.storage)
        except InvalidParameterException as error:
            if default is None:
                raise error

            return default

    def get_servers(self, server_type):
        if server_type not in (SERVER_WEB, SERVER_BOT, SERVER_MAINTAIN):
            raise InvalidParameterException(
                'Invalid server type "{}"'.format(server_type)
            )

        # deploy on cluster
        if CLUSTER in self.storage['place']:
            return self.storage['place'][CLUSTER]

        # deploy on cloud
        if server_type not in self.storage['place'][CLOUD]:
            return []

        return self.storage['place'][CLOUD][server_type]

    def get_hosts(self, host_type):
        if host_type not in (HOST_WEB, HOST_BOT, HOST_MAINTAIN, HOST_ALL):
            raise InvalidParameterException(
                'Invalid host type "{}"'.format(host_type)
            )

        # deploy on cluster
        if CLUSTER in self.storage['place']:
            return get_hosts(self.storage['place'][CLUSTER])

        # deploy on cloud
        iteration_types = [host_type]
        if host_type == HOST_ALL:
            iteration_types = (HOST_WEB, HOST_BOT, HOST_MAINTAIN)

        hosts = []
        for iteration_type in iteration_types:
            if iteration_type not in self.storage['place'][CLOUD]:
                continue

            for server in self.storage['place'][CLOUD][iteration_type]:
                hosts.append(server['host'])

        return hosts

    def is_cluster_mode(self):
        if CLUSTER in self.storage['place']:
            return True

        return False
