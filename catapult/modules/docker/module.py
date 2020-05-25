import docker
from catapult.deploy.constants import REGISTER_CHECK, REGISTER_INSTALL, REGISTER_WEB_AND_BOT
from catapult.modules.normalizers import normalize_docker
from catapult.library.exceptions import ModuleException
from catapult.library.renders import render_path


class Module:
    def __init__(self, module_config, storage, paths, register, logger):
        if not storage.get('place.registry'):
            raise ModuleException(
                'You must specify section "registry" in config.yml of service "{}"'.format(
                    storage.get('release.service')
                )
            )

        if 'publish' not in module_config:
            module_config['publish'] = []

        if not isinstance(module_config['publish'], list):
            module_config['publish'] = [module_config['publish']]

        self.module_config = module_config
        self.storage = storage
        self.paths = paths
        self.logger = logger
        self.register = register

        self.tag = "{}:{}".format(storage.get('place.registry'), storage.get('release.name'))

        register(REGISTER_CHECK, REGISTER_WEB_AND_BOT, self.render_check())

    def render_check(self):
        path = '{}/docker/check.j2'.format(
            self.paths.get('catapult.templates'),
        )

        generated = render_path(path, {
            'storage': self.storage.get,
            'paths': self.paths.get,
        })

        return generated

    def configure(self, config):
        config = normalize_docker(config)

        self.register(REGISTER_INSTALL, REGISTER_WEB_AND_BOT, self.render_install(config['workdir']))

        build_image(
            config,
            self.tag,
            self.paths,
            self.storage,
            self.logger
        )

    def render_install(self, workdir):
        path = '{}/docker/install.j2'.format(
            self.paths.get('catapult.templates'),
        )

        volumes = render_volumes(
            workdir,
            self.paths,
            self.storage
        )

        publish = self.render_publish()

        container = 'catapult-{}-{}'.format(
            self.storage.get('release.service'),
            self.storage.get('release.place')
        )

        generated = render_path(path, {
            'container': container,
            'tag': self.tag,
            'server': self.storage.get('config.registry.server'),
            'username': self.storage.get('config.registry.username'),
            'password': self.storage.get('config.registry.password'),
            'volumes': volumes,
            'publish': publish,
        })

        return generated

    def render_publish(self):
        if not self.module_config['publish']:
            self.logger.info('docker mapping ports skipped')

            return ''

        self.logger.info('docker using mapping ports {}'.format(', '.join(self.module_config['publish'])))

        path_publish = '{}/docker/publish.j2'.format(
            self.paths.get('catapult.templates'),
        )

        publications = []

        for publish in self.module_config['publish']:
            generated = render_path(path_publish, {
                'publish': publish,
            })

            publications.append(generated)

        return ' '.join(publications)


def render_volumes(workdir, paths, storage):
    path_volume = '{}/docker/volume.j2'.format(
        paths.get('catapult.templates'),
    )

    shared_folder = "{}/{}/shared".format(
        storage.get('config.deploy.deploy_path'),
        storage.get('release.service')
    )

    volumes = []

    for linked in storage.get('place.linked'):
        from_path = "{}/{}".format(
            shared_folder,
            linked
        )

        to_path = "{}/{}".format(
            workdir.rstrip('/'),
            linked
        )

        generated = render_path(path_volume, {
            'from': from_path,
            'to': to_path,
        })

        volumes.append(generated)

    return '\n'.join(volumes)

def build_image(config, tag, paths, storage, logger):
    client = docker.DockerClient(base_url=storage.get('config.registry.base_url'))

    logger.info('building docker image with tag %s' % tag)

    buildargs = {
        **storage.get('parameters'),
        **config['buildargs']
    }

    try:
        generator = client.images.build(
            path=paths.get('local.code'),
            dockerfile=config['dockerfile'],
            tag=tag,
            nocache=False,
            forcerm=True,
            buildargs=buildargs,
            rm=True
        )
    except docker.errors.BuildError as e:
        for line in e.build_log:
            if 'stream' in line:
                logger.error(line['stream'].strip())

        raise ModuleException('Some error occurred while building docker image')

    logger.info('docker image successfully built, pushing to remote registry')

    auth_config = {
        'username': storage.get('config.registry.username'),
        'password': storage.get('config.registry.password'),
    }

    pushing_stream = client.images.push(
        tag,
        auth_config=auth_config,
        stream=True,
        decode=True
    )

    for line in pushing_stream:
        if 'status' in line:
            logger.info(line['status'].strip())