from catapult.server.builders import fail_response
from catapult.server.constants import INVALID_TOKEN


def check_token(f):
    def wrapper(self, *args, **kwargs):
        if 'X-Token' not in self.request.headers:
            self.write(fail_response(
                INVALID_TOKEN,
                'You must specify X-Token header'
            ))

            return

        if self.request.headers['X-Token'] != self.token:
            self.write(fail_response(
                INVALID_TOKEN,
                'This token is incorrect'
            ))

            return

        f(self, *args, **kwargs)

    return wrapper
