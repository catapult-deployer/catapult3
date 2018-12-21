import os
from catapult.library.renders import render_path
from catapult.library.exceptions import LockException


class Locker:
    def __init__(self, paths, storage, ssh, logger):
        self.paths = paths
        self.storage = storage
        self.ssh = ssh
        self.logger = logger

        self.lock_path = '/tmp/locker_{}.sh'.format(storage.get('release.name'))

    def acquire_lock(self):
        template_path = '{}/core/lock.j2'.format(
            self.paths.get('catapult.templates')
        )

        generated = render_path(template_path, {
            'service_folder': self.paths.get('remote.service_folder'),
            'release_name': self.storage.get('release.name')
        })

        file = '{}/locker.sh'.format(self.paths.get('local.release'))
        with open(file, 'w') as open_file:
            open_file.write(generated)

        os.chmod(file, 0o766)

        self.logger.info('move lock file to all hosts')

        self.ssh.move_on_hosts(
            '{}/locker.sh'.format(self.paths.get('local.release')),
            self.lock_path
        )
        self.ssh.execute_on_hosts('chmod +x {}'.format(self.lock_path))

        self.logger.info('moving lock file to all hosts completed')

        self.logger.info('start executing locking on hosts')

        # if is force deploy
        if self.storage.get('release.force'):
            self.logger.info('release old lock because is force deploy')

            self.release_lock()

        locks = self.ssh.execute_on_hosts('{} acquire_lock'.format(self.lock_path))

        self.logger.info('executing locking on hosts completed')

        for host, result in locks.items():
            if not result:
                raise LockException(
                    'Can not get result about acquire lock. Stdout lock from host "{}" is empty'.format(host)
                )

            if result != 'true':
                raise LockException(
                    'Can not obtain lock on host "{}", result is "{}"'.format(host, result)
                )

        # check equivalent releases on all hosts

        # if is force deploy
        if self.storage.get('release.force'):
            return True

        releases = self.ssh.execute_on_hosts('"{}" get_current_release'.format(self.lock_path))

        release = None
        for host, current_release in releases.items():
            if not current_release:
                raise LockException(
                    'Can not get current_release. Stdout lock from host "{}" is empty.'.format(host)
                )

            if release is None:
                release = current_release

            if release != current_release:
                raise LockException(
                    'Release "{}" not compared for host "{}" release "{}"'.format(release, host, current_release)
                )

    def release_lock(self):
        locks = self.ssh.execute_on_hosts('{} release_lock'.format(self.lock_path))

        for host, result in locks.items():
            if not result:
                raise LockException(
                    'Can not get result about release lock. Stdout lock from host "{}" is empty'.format(host)
                )

            if result != 'true':
                raise LockException(
                    'Can not obtain lock on host "{}", result is "{}"'.format(host, result)
                )

            if not self.storage.get('release.force') and result != 'true':
                raise LockException(
                    'Can not release lock on host "{}", result is "{}"'.format(host, result)
                )
