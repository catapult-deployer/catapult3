import time
from catapult.deploy.constants import TRANSPORT_PUSHOVER, TRANSPORT_SLACK, TRANSPORT_TELEGRAM
from catapult.library.renders import render_string
from catapult.library.transports import pushover, telegram, slack


class Notifier:
    def __init__(self, notifications, request, logger):
        self.notifications = notifications
        self.request = request
        self.logger = logger

    def notify(self, is_success=True):
        if not self.notifications:
            return

        for transport, config in self.notifications.items():
            if not config:
                continue

            message = self.get_message(
                is_success,
                config['messages']['success'],
                config['messages']['fail']
            )

            if transport == TRANSPORT_TELEGRAM:
                try:
                    self.logger.info('try to deliver message with transport Telegram')

                    telegram(
                        config['token'],
                        config['chat_id'],
                        message
                    )

                    self.logger.success('message sent')
                except Exception as error:
                    self.logger.error(error)

            if transport == TRANSPORT_PUSHOVER:
                try:
                    self.logger.info('try to deliver message with transport Pushover')

                    for client in config['clients']:
                        pushover(
                            config['token'],
                            client,
                            message
                        )

                    self.logger.success('message sent')
                except Exception as error:
                    self.logger.error(error)

            if transport == TRANSPORT_SLACK:
                try:
                    self.logger.info('try to deliver message with transport Slack')

                    slack(
                        config['token'],
                        config['channel'],
                        message
                    )

                    self.logger.success('message sent')
                except Exception as error:
                    self.logger.error(error)

    def get_message(self, is_success, success, fail):
        self.request['time'] = round(int(time.time()) - self.request['time_start'], 2)

        template = success if is_success else fail

        return render_string(template, self.request)
