from os import makedirs, remove
from os.path import exists
from catapult.library.exceptions import BlockerException


class Blocker:
    def __init__(self, releases_folder, release_place, release_name):
        self.release_name = release_name

        if not exists(releases_folder):
            makedirs(releases_folder)

        self.lock_file = '{}/.{}.lock'.format(
            releases_folder,
            release_place
        )

    def acquire_lock(self):
        if exists(self.lock_file):
            raise BlockerException(
                'Can not obtain local lock by path "{}"'.format(self.lock_file)
            )

        with open(self.lock_file, 'w') as lock_file:
            lock_file.write(self.release_name)

    def release_lock(self):
        try:
            remove(self.lock_file)
        except:
            pass

