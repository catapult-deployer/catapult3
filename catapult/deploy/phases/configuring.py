import re
import yaml
import shutil
import codecs
from git import Repo
from os import makedirs, walk
from os.path import isfile, expanduser, exists, isdir, join
from catapult.library.exceptions import DeployException
from catapult.library.renders import render_shared, render_path
from catapult.deploy.modules import Modules
from catapult.deploy.constants import HOST_ALL


def phase(paths, storage, _, __, ___, logger):
    # cloning repo
    logger.info('cloning repo "{}" with key_file by path "{}"'.format(
        storage.get('place.repo'),
        storage.get('config.deploy.git.key_file')
    ))

    git_ssh_identity_file = expanduser(storage.get('config.deploy.git.key_file'))
    git_ssh_cmd = 'ssh -i {}'.format(git_ssh_identity_file)

    Repo.clone_from(
        storage.get('place.repo'),
        paths.get('local.code'),
        branch=storage.get('release.branch'),
        env=dict(GIT_SSH_COMMAND=git_ssh_cmd)
    )

    # remove .git folder
    shutil.rmtree('{}/.git'.format(paths.get('local.code')))

    parse_deploy_yaml(storage, paths, logger)
    configure_shared(storage, paths, logger)
    configure_templates(storage, paths, logger)


def parse_deploy_yaml(storage, paths, logger):
    deploy_yaml = {}

    path = '{}/deploy.yml'.format(paths.get('local.code'))

    if not isfile(path):
        logger.warning('deploy.yml file does not exist, skipped')
    else:
        with open(path) as stream:
            try:
                deploy_yaml = yaml.load(stream, Loader=yaml.Loader)
            except Exception as error:
                raise DeployException(
                    'An error occurred "{}" with parsing deploy.yml file by path "{}"'.format(error, path)
                )

    # configure modules
    modules = Modules(storage, paths, logger)
    modules.configure(deploy_yaml)


def configure_shared(storage, paths, logger):
    for host in storage.get_hosts(HOST_ALL):
        logger.info('configuring shared folder for host "{}"'.format(host))

        path_host = '{}/{}'.format(
            paths.get('local.shared'),
            host
        )

        if not exists(path_host):
            makedirs(path_host)

        path_service = '{}/{}/shared'.format(
            paths.get('local.services'),
            storage.get('release.service')
        )

        if not exists(path_service):
            logger.info('shared folder for service does not exist, skipped')

            continue

        pattern = re.compile(r'\.\[([^]]+)\]')

        for root, dirs, files in walk(path_service, topdown=True):
            path = root.replace(path_service, path_host)

            if not isdir(path):
                makedirs(path)

            for name in files:
                modifiers = re.findall(pattern, name)

                if not is_place_fit(modifiers, storage.get('release.place')):
                    logger.info('shared template file "{}" does not fit'.format(name))

                    continue

                cleaned = name
                for modifier in modifiers:
                    cleaned = cleaned.replace('.[{}]'.format(modifier), '')

                file_src = join(root, name)
                file_dest = join(path, cleaned)

                logger.info('copy shared from "{}" -> to -> "{}" to host "{}"'.format(
                    name,
                    cleaned,
                    host
                ))

                render_shared(
                    file_src,
                    file_dest,
                    storage,
                    paths,
                    host
                )


def configure_templates(storage, paths, logger):
    code_path = paths.get('local.code')

    for root, dirs, files in walk(code_path):
        for name in files:
            extension = name[-9:]

            if extension != '.catapult':
                continue

            cleaned = name[:-9]

            file_src = join(root, name)
            file_dest = join(root, cleaned)

            logger.info('configured template file "{}"'.format(file_src))

            generated = render_path(file_src, {
                'get': storage.get,
                'storage': storage.get,
                'paths': paths.get,
            })

            with codecs.open(file_dest, 'w', encoding='utf8') as open_file:
                open_file.write(generated)


def is_place_fit(modifiers, place):
    if len(modifiers) == 0:
        return True

    if place in modifiers:
        return True

    is_consist_not = False
    for modifier in modifiers:
        if modifier[0] == '!':
            is_consist_not = True

            if modifier == '!' + place:
                return False

    return is_consist_not
