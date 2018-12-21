import tarfile
from os import makedirs, walk
from multiprocessing import Process
from catapult.deploy.constants import HOST_ALL


def phase(paths, storage, _, __, ___, logger):
    hosts = storage.get_hosts(HOST_ALL)

    makedirs(paths.get('local.builds'))

    processes = {}

    for host in hosts:
        logger.info('start creating build for host "{}"'.format(host))

        process = Process(target=create_build, args=(host, paths))
        process.start()

        processes[host] = process

    for host in hosts:
        processes[host].join()

        logger.success('build for host "{}" created'.format(host))


def create_build(host, paths):
    path_tar = '{}/{}.tar.gz'.format(
        paths.get('local.builds'),
        host
    )

    path_shared = '{}/{}'.format(
        paths.get('local.shared'),
        host
    )

    tar = tarfile.open(path_tar, 'w:gz')

    tar.add(
        '{}/install.sh'.format(paths.get('local.release')),
        arcname='install.sh'
    )

    tar.add(
        path_shared,
        arcname='shared'
    )

    tar.add(
        paths.get('local.code'),
        arcname='code'
    )

    for root, dirs, files in walk('{}/{}'.format(paths.get('local.configs'), host), topdown=True):
        for file in files:
            tar.add(
                '{}/{}'.format(root, file),
                arcname='configs/{}'.format(file)
            )

    tar.close()
