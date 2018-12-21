import json


def success_response(data):
    response = {
        'isSuccess': True,
        'data': data
    }

    return json.dumps(response)


def fail_response(code, message):
    response = {
        'isSuccess': False,
        'error': {
            'code': code,
            'message': message
        }
    }

    return json.dumps(response)


def event_input(event_type, payload={}):
    data = {
        'event': event_type,
        'payload': payload,
    }

    return json.dumps(data)


def event_error(code, message):
    data = {
        'event': 'error',
        'payload': {
            'code': code,
            'message': message,
        },
    }

    return json.dumps(data)
