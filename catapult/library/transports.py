import requests


def pushover(api_token, client_token, message):
    requests.post(
        'https://api.pushover.net/1/messages.json',
        data={
            'token': api_token,
            'user': client_token,
            'title': 'Catapult',
            'message': message,
            'sound': 'bugle',
        }
    )


def telegram(api_token, chat_id, message):
    payload = dict(
        chat_id=chat_id,
        text=message
    )

    requests.get(
        'https://api.telegram.org/bot{}/sendMessage'.format(api_token),
        params=payload
    )


def slack(api_token, channel, message):
    requests.post(
        'https://slack.com/api/chat.postMessage',
        data={
            'token': api_token,
            'channel': channel,
            'text': message,
        }
    )
