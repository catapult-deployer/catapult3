import re
from catapult.library.exceptions import ModuleException
from catapult.modules.constants import BOT_BALANCING, BOT_MIRRORING
from catapult.deploy.constants import SERVER_WEB, SERVER_BOT
from catapult.modules.constants import MODE_CLUSTER, MODE_FORK


def normalize_nginx(config):
    if 'root' not in config:
        raise ModuleException('You must specify section "root" for "nginx" section in deploy.yml')

    if 'index_files' not in config:
        raise ModuleException('You must specify section "index_files" for "nginx" section in deploy.yml')

    if not isinstance(config['index_files'], list):
        raise ModuleException('Section "index_files" for "nginx" section in deploy.yml must be a list')

    if 'locations' not in config:
        config['locations'] = []

    locations = []

    for location in config['locations']:
        if 'match' not in location:
            raise ModuleException('You must specify section "match" for locations in deploy.yml')

        if 'modifier' not in location:
            location['modifier'] = ''

        if 'configs' not in location:
            raise ModuleException('You must specify section "configs" for location "{}" in deploy.yml'.format(
                location['match']
            ))

        if not isinstance(location['configs'], dict):
            raise ModuleException('Section "configs" for "nginx" section in deploy.yml must be dictionary')

        locations.append(location)

    config['locations'] = locations

    return config


def normalize_crons(crons):
    is_weight_set = False
    for cron in crons:
        if 'command' not in cron:
            raise ModuleException('You must specify "command" section for all cron commands in deploy.yml')

        if 'planning' not in cron:
            raise ModuleException('You must specify "planning" section for all cron commands in deploy.yml')

        if not isinstance(cron['planning'], dict):
            raise ModuleException('Section "planning" for cron command in deploy.yml must be dictionary')

        # validate minutes, hours, dom, mon, dow
        for item in ('minutes', 'hours', 'dom', 'mon', 'dow'):
            if item not in cron['planning']:
                raise ModuleException(
                    'You must specify "{}" section for cron command "{}" in deploy.yml'.format(
                        item,
                        cron['command'],
                    )
                )

        # validate weight section
        if 'weight' in cron:
            if not isinstance(cron['weight'], int):
                raise ModuleException(
                    'Section "weight" for cron command "{}" in deploy.yml must be integer'.format(
                        cron['command'],
                    )
                )

            is_weight_set = True

        if 'weight' not in cron and is_weight_set is True:
            raise ModuleException(
                'You must specify "weight" for cron command "{}" in deploy.yml'.format(
                    cron['command'],
                )
            )

        if is_weight_set is True and (cron['weight'] > 3 or cron['weight'] <= 0):
            raise ModuleException(
                'Section "weight" for cron command "{}" in deploy.yml must be between 1 and 3'.format(
                    cron['command'],
                )
            )

        # transform weight section
        if 'weight' not in cron:
            cron['weight'] = 1

    return crons


def normalize_supervisor(demons):
    allowed = (BOT_BALANCING, BOT_MIRRORING)
    pattern_validate = '^[a-zA-Z0-9_:\- ]+$'
    regular_validate = re.compile(pattern_validate)

    pattern_clean = '[^a-z0-9]+'
    regular_clean = re.compile(pattern_clean)

    names = []
    is_weight_set = False
    for demon in demons:
        if 'name' not in demon:
            raise ModuleException('You must specify "name" section for all supervisor demons in deploy.yml')

        if not regular_validate.match(demon['name']):
            raise ModuleException(
                'Name "{}" for supervisor demon must match to pattern "{}" in deploy.yml'.format(
                    demon['name'],
                    pattern_validate
                )
            )

        demon['name'] = demon['name'].lower()
        demon['name'] = regular_clean.sub('_', demon['name'])

        if demon['name'] in names:
            raise ModuleException(
                'Name "{}" for supervisor demon already exists in deploy.yml'.format(
                    demon['name']
                )
            )

        names.append(demon['name'])

        if 'command' not in demon:
            raise ModuleException(
                'You must specify "command" section for supervisor demon "{}" in deploy.yml'.format(
                    demon['name']
                )
            )

        if 'instances' not in demon:
            raise ModuleException(
                'You must specify "instances" section for supervisor demon "{}" in deploy.yml'.format(
                    demon['name']
                )
            )

        if not isinstance(demon['instances'], int):
            raise ModuleException(
                'Section "instances" for supervisor demon "{}" in deploy.yml must be integer'.format(
                    demon['name'],
                )
            )

        if demon['instances'] <= 0:
            raise ModuleException(
                'Section "instances" for supervisor demon "{}" in deploy.yml must be more than 0'.format(
                    demon['name'],
                )
            )

        if 'type' not in demon:
            raise ModuleException(
                'You must specify "type" section for supervisor demon "{}" in deploy.yml'.format(
                    demon['name']
                )
            )

        if demon['type'] not in allowed:
            raise ModuleException(
                'Section "type" for supervisor demon "{}" in deploy.yml must by {}'.format(
                    demon['name'],
                    ' or '.join(allowed)
                )
            )

        # validate weight section
        if 'weight' in demon:
            if not isinstance(demon['weight'], int):
                raise ModuleException(
                    'Section "weight" for supervisor demon "{}" in deploy.yml must be integer'.format(
                        demon['name'],
                    )
                )

            is_weight_set = True

        if 'weight' not in demon and is_weight_set is True:
            raise ModuleException(
                'You must specify "weight" for supervisor demon "{}" in deploy.yml'.format(
                    demon['name'],
                )
            )

        if is_weight_set is True and (demon['weight'] > 3 or demon['weight'] <= 0):
            raise ModuleException(
                'Section "weight" for supervisor demon "{}" in deploy.yml must be between 1 and 3'.format(
                    demon['name'],
                )
            )

        # transform weight section
        if 'weight' not in demon:
            demon['weight'] = 1

    return demons


def normalize_systemd(config):
    if 'execute' not in config:
        raise ModuleException('You must specify section "execute" for "systemd" section in deploy.yml')

    if 'environments' not in config:
        config['environments'] = {}

    if 'environments' in config:
        if not isinstance(config['environments'], dict):
            raise ModuleException('Section "environments" for "systemd" section in deploy.yml must be a dict')

    return config


def normalize_pm2(service_name, applications):
    allowed_modes = (MODE_CLUSTER, MODE_FORK)
    allowed_servers = (SERVER_WEB, SERVER_BOT)
    allowed_types = (BOT_BALANCING, BOT_MIRRORING)
    pattern_validate = '^[a-zA-Z0-9_:\- ]+$'
    regular_validate = re.compile(pattern_validate)

    pattern_clean = '[^a-z0-9]+'
    regular_clean = re.compile(pattern_clean)

    names = []
    is_weight_set = False
    for application in applications:
        if 'name' not in application:
            raise ModuleException('You must specify "name" section for all pm2 applications in deploy.yml')

        if not regular_validate.match(application['name']):
            raise ModuleException(
                'Name "{}" for pm2 application must match to pattern "{}" in deploy.yml'.format(
                    application['name'],
                    pattern_validate
                )
            )

        application['name'] = '{}-{}'.format(
            service_name,
            application['name']
        )
        application['name'] = application['name'].lower()
        application['name'] = regular_clean.sub('_', application['name'])

        if application['name'] in names:
            raise ModuleException(
                'Name "{}" for pm2 application already exists in deploy.yml'.format(
                    application['name']
                )
            )

        names.append(application['name'])

        if 'mode' not in application:
            raise ModuleException(
                'You must specify "mode" section for pm2 application "{}" in deploy.yml'.format(
                    application['name']
                )
            )

        if application['mode'] not in allowed_modes:
            raise ModuleException(
                'Section "mode" for pm2 application "{}" in deploy.yml must by {}'.format(
                    application['name'],
                    ' or '.join(allowed_modes)
                )
            )

        if 'command' not in application:
            raise ModuleException(
                'You must specify "command" section for pm2 application "{}" in deploy.yml'.format(
                    application['name']
                )
            )

        if 'instances' not in application:
            raise ModuleException(
                'You must specify "instances" section for pm2 application "{}" in deploy.yml'.format(
                    application['name']
                )
            )

        if not isinstance(application['instances'], int):
            raise ModuleException(
                'Section "instances" for pm2 application "{}" in deploy.yml must be integer'.format(
                    application['name'],
                )
            )

        if application['instances'] <= 0:
            raise ModuleException(
                'Section "instances" for pm2 application "{}" in deploy.yml must be more than 0'.format(
                    application['name'],
                )
            )

        if 'server' not in application:
            raise ModuleException(
                'You must specify "server" section for pm2 application "{}" in deploy.yml'.format(
                    application['name']
                )
            )

        if application['server'] not in allowed_servers:
            raise ModuleException(
                'Section "server" for pm2 application "{}" in deploy.yml must by {}'.format(
                    application['name'],
                    ' or '.join(allowed_servers)
                )
            )

        if application['server'] == SERVER_BOT:
            if 'type' not in application:
                raise ModuleException(
                    'You must specify "type" section for pm2 bot application "{}" in deploy.yml'.format(
                        application['name'],
                    )
                )

            if application['type'] not in allowed_types:
                raise ModuleException(
                    'Section "type" for pm2 bot application "{}" in deploy.yml must by {}'.format(
                        application['name'],
                        ' or '.join(allowed_types)
                    )
                )

        # validate weight section
        if 'weight' in application:
            if not isinstance(application['weight'], int):
                raise ModuleException(
                    'Section "weight" for pm2 application "{}" in deploy.yml must be integer'.format(
                        application['name'],
                    )
                )

            is_weight_set = True

        if 'weight' not in application and is_weight_set is True:
            raise ModuleException(
                'You must specify "weight" for pm2 application "{}" in deploy.yml'.format(
                    application['name'],
                )
            )

        if is_weight_set is True and (application['weight'] > 3 or application['weight'] <= 0):
            raise ModuleException(
                'Section "weight" for pm2 application "{}" in deploy.yml must be between 1 and 3'.format(
                    application['name'],
                )
            )

        # transform weight section
        if 'weight' not in application:
            application['weight'] = 1

    return applications


def normalize_docker(config):
    if 'dockerfile' not in config:
        raise ModuleException('You must specify section "dockerfile" for "docker" section in deploy.yml')

    if 'workdir' not in config:
        raise ModuleException('You must specify section "workdir" for "docker" section in deploy.yml')

    if 'buildargs' not in config:
        config['buildargs'] = {}

    if 'buildargs' in config:
        if not isinstance(config['buildargs'], dict):
            raise ModuleException('Section "buildargs" for "docker" section in deploy.yml must be a dict')

    return config
