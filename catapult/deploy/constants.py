LOGGER_INFO = 'info'
LOGGER_ERROR = 'error'
LOGGER_SUCCESS = 'success'
LOGGER_WARNING = 'warning'
LOGGER_PHASE = 'phase'

CLUSTER = 'cluster'
CLOUD = 'cloud'

STATE_BEFORE = 'before'
STATE_AFTER = 'after'

TRANSPORT_TELEGRAM = 'telegram'
TRANSPORT_SLACK = 'slack'
TRANSPORT_PUSHOVER = 'pushover'

BULLET_LOCAL = 'local'
BULLET_REMOTE = 'remote'
BULLET_MAINTAIN = 'maintain'
BULLET_CONSOLE = 'console'

SERVER_WEB = 'web'
SERVER_BOT = 'bot'
SERVER_MAINTAIN = 'maintain'

HOST_ALL = 'all'
HOST_WEB = 'web'
HOST_BOT = 'bot'
HOST_MAINTAIN = 'maintain'

REGISTER_WEB = 'web'
REGISTER_BOT = 'bot'
REGISTER_WEB_AND_BOT = 'web_and_bot'
REGISTER_CHECK = 'check'
REGISTER_INSTALL = 'install'

PHASES = [
    'starting',
    'locking',
    'configuring',
    'building',
    'checking',
    'releasing',
    'maintaining',
    'installing',
    'cleaning',
    'ending',
]
