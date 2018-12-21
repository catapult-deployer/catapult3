import logging
from tornado.web import RequestHandler
from catapult.server.builders import success_response, fail_response
from catapult.server.constants import INVALID_RELEASE
from catapult.server.routes.check_token import check_token


class GetRelease(RequestHandler):
    def initialize(self, token, repository):
        self.token = token
        self.repository = repository

    @check_token
    def get(self, release_name):
        logging.info('get information about release {}'.format(release_name))

        release = self.repository.get_release(release_name)

        if not release:
            self.write(fail_response(INVALID_RELEASE, 'Release with name {} does not found'.format(release_name)))

            return

        self.write(success_response(release))
