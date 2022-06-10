# Configuration file for application.

# ------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
# ------------------------------------------------------------------------------
## This is an application.

## The date format used by logging formatters for %(asctime)s
#  Default: '%Y-%m-%d %H:%M:%S'
# c.Application.log_datefmt = '%Y-%m-%d %H:%M:%S'

## The Logging format template
#  Default: '[%(name)s]%(highlevel)s %(message)s'
# c.Application.log_format = '[%(name)s]%(highlevel)s %(message)s'

## Set the log level by value or name.
#  Choices: any of [0, 10, 20, 30, 40, 50, 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
#  Default: 30
# c.Application.log_level = 30

## Configure additional log handlers.
#
#  The default stderr logs handler is configured by the log_level, log_datefmt
#  and log_format settings.
#
#  This configuration can be used to configure additional handlers (e.g. to
#  output the log to a file) or for finer control over the default handlers.
#
#  If provided this should be a logging configuration dictionary, for more
#  information see:
#  https://docs.python.org/3/library/logging.config.html#logging-config-
#  dictschema
#
#  This dictionary is merged with the base logging configuration which defines
#  the following:
#
#  * A logging formatter intended for interactive use called
#    ``console``.
#  * A logging handler that writes to stderr called
#    ``console`` which uses the formatter ``console``.
#  * A logger with the name of this application set to ``DEBUG``
#    level.
#
#  This example adds a new handler that writes to a file:
#
#  .. code-block:: python
#
#     c.Application.logging_configuration = {
#         'handlers': {
#             'file': {
#                 'class': 'logging.FileHandler',
#                 'level': 'DEBUG',
#                 'filename': '<path/to/file>',
#             }
#         },
#         'loggers': {
#             '<application-name>': {
#                 'level': 'DEBUG',
#                 # NOTE: if you don't list the default "console"
#                 # handler here then it will be disabled
#                 'handlers': ['console', 'file'],
#             },
#         }
#     }
#  Default: {}
# c.Application.logging_config = {}

## Instead of starting the Application, dump configuration to stdout
#  Default: False
# c.Application.show_config = False

## Instead of starting the Application, dump configuration to stdout (as JSON)
#  Default: False
# c.Application.show_config_json = False

# ------------------------------------------------------------------------------
# AnnouncementService(Application) configuration
# ------------------------------------------------------------------------------
## This is an application.

## Allow access from subdomains
#  Default: False
# c.AnnouncementService.allow_origin = False

## Config file to load
#  Default: 'announcement_config.py'
# c.AnnouncementService.config_file = 'announcement_config.py'

## File in which we store the cookie secret.
#  Default: 'jupyterhub-announcement-cookie-secret'
# c.AnnouncementService.cookie_secret_file = 'jupyterhub-announcement-cookie-secret'

## Async callable to add extra info to the latest announcement.
#  Default: None
# c.AnnouncementService.extra_info_hook = None

## Fixed message to show at the top of the page.
#
#           A good use for this parameter would be a link to a more general
#           live system status page or MOTD.
#  Default: ''
# c.AnnouncementService.fixed_message = ''

## Generate default config file
#  Default: False
# c.AnnouncementService.generate_config = False

## The date format used by logging formatters for %(asctime)s
#  See also: Application.log_datefmt
# c.AnnouncementService.log_datefmt = '%Y-%m-%d %H:%M:%S'

## The Logging format template
#  See also: Application.log_format
# c.AnnouncementService.log_format = '[%(name)s]%(highlevel)s %(message)s'

## Set the log level by value or name.
#  See also: Application.log_level
# c.AnnouncementService.log_level = 30

##
#  See also: Application.logging_config
# c.AnnouncementService.logging_config = {}

## Logo path, can be used to override JupyterHub one
#  Default: ''
# c.AnnouncementService.logo_file = ''

## Port this service will listen on
#  Default: 8888
# c.AnnouncementService.port = 8888

## Announcement service prefix
#  Default: '/services/announcement/'
# c.AnnouncementService.service_prefix = '/services/announcement/'

## Instead of starting the Application, dump configuration to stdout
#  See also: Application.show_config
# c.AnnouncementService.show_config = False

## Instead of starting the Application, dump configuration to stdout (as JSON)
#  See also: Application.show_config_json
# c.AnnouncementService.show_config_json = False

## Search paths for jinja templates, coming before default ones
#  Default: []
# c.AnnouncementService.template_paths = []

# ------------------------------------------------------------------------------
# AnnouncementQueue(LoggingConfigurable) configuration
# ------------------------------------------------------------------------------
## Number of days to retain announcements.
#
#          Announcements that have been in the queue for this many days are
#          purged from the queue.
#  Default: 7.0
# c.AnnouncementQueue.lifetime_days = 7.0

## File path where announcements persist as JSON.
#
#          For a persistent announcement queue, this parameter must be set to
#          a non-empty value and correspond to a read+write-accessible path.
#          The announcement queue is stored as a list of JSON objects. If this
#          parameter is set to a non-empty value:
#
#          * The persistence file is used to initialize the announcement queue
#            at start-up. This is the only time the persistence file is read.
#          * If the persistence file does not exist at start-up, it is
#            created when an announcement is added to the queue.
#          * The persistence file is over-written with the contents of the
#            announcement queue each time a new announcement is added.
#
#          If this parameter is set to an empty value (the default) then the
#          queue is just empty at initialization and the queue is ephemeral;
#          announcements will not be persisted on updates to the queue.
#  Default: ''
# c.AnnouncementQueue.persist_path = ''

# ------------------------------------------------------------------------------
# SSLContext(Configurable) configuration
# ------------------------------------------------------------------------------
## SSL CA, use with keyfile and certfile
#  Default: ''
# c.SSLContext.cafile = ''

## SSL cert, use with keyfile
#  Default: ''
# c.SSLContext.certfile = ''

## SSL key, use with certfile
#  Default: ''
# c.SSLContext.keyfile = ''
