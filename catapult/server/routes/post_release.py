import logging
from json import loads
from tornado.web import RequestHandler
from catapult.server.builders import success_response, fail_response
from catapult.server.constants import INVALID_JSON, INVALID_REQUEST, DEPLOY_PENDING
from catapult.library.transformers import saturate_request, transform_server_request
from catapult.library.validators import validate_request
from catapult.library.exceptions import InvalidRequestException
from catapult.server.routes.check_token import check_token


class PostRelease(RequestHandler):
    def initialize(self, token, services, deploy_queue, write_queue):
        self.token = token
        self.services = services
        self.deploy_queue = deploy_queue
        self.write_queue = write_queue

    @check_token
    def post(self):
        try:
            request = loads(self.request.body.decode('utf-8'))
        except Exception as error:
            self.write(fail_response(INVALID_JSON, 'An error occurred with parsing json: {}'.format(error)))
            return

        request = transform_server_request(request)
        request = saturate_request(request)

        try:
            validate_request(request, self.services)
        except InvalidRequestException as error:
            self.write(fail_response(INVALID_REQUEST, str(error)))
            return

        logging.info('handle request {}'.format(request))

        self.write_queue.put({
            'name': request['name'],
            'status': DEPLOY_PENDING,
            'request': request,
        })
        self.deploy_queue.put(request)

        data = {
            'release_name': request['name']
        }

        self.write(success_response(data))
