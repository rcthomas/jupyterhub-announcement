# Configuration file for application.

#------------------------------------------------------------------------------
# Application(SingletonConfigurable) configuration
#------------------------------------------------------------------------------

## This is an application.

## The date format used by logging formatters for %(asctime)s
#c.Application.log_datefmt = '%Y-%m-%d %H:%M:%S'

## The Logging format template
#c.Application.log_format = '[%(name)s]%(highlevel)s %(message)s'

## Set the log level by value or name.
#c.Application.log_level = 30

#------------------------------------------------------------------------------
# AnnouncementService(Application) configuration
#------------------------------------------------------------------------------

## This is an application.

## Config file to load
#c.AnnouncementService.config_file = 'announcement_config.py'

## Fixed message to show at the top of the page.
#  
#  A good use for this parameter would be a link to a more general live system
#  status page or MOTD.
#c.AnnouncementService.fixed_message = ''

## Generate default config file
#c.AnnouncementService.generate_config = False

## Logo path, can be used to override JupyterHub one
#c.AnnouncementService.logo_file = ''

## Port this service will listen on
#c.AnnouncementService.port = 8888

## Announcement service prefix
#c.AnnouncementService.service_prefix = '/services/announcement/'

## Search paths for jinja templates, coming before default ones
#c.AnnouncementService.template_paths = []

#------------------------------------------------------------------------------
# AnnouncementQueue(LoggingConfigurable) configuration
#------------------------------------------------------------------------------

## Number of days to retain announcements.
#  
#  Announcements that have been in the queue for this many days are purged from
#  the queue.
#c.AnnouncementQueue.lifetime_days = 7.0

## File path where announcements persist as JSON.
#  
#  For a persistent announcement queue, this parameter must be set to a non-empty
#  value and correspond to a read+write-accessible path. The announcement queue
#  is stored as a list of JSON objects. If this parameter is set to a non-empty
#  value:
#  
#  * The persistence file is used to initialize the announcement queue
#    at start-up. This is the only time the persistence file is read.
#  * If the persistence file does not exist at start-up, it is
#    created when an announcement is added to the queue.
#  * The persistence file is over-written with the contents of the
#    announcement queue each time a new announcement is added.
#  
#  If this parameter is set to an empty value (the default) then the queue is
#  just empty at initialization and the queue is ephemeral; announcements will
#  not be persisted on updates to the queue.
#c.AnnouncementQueue.persist_path = ''

#------------------------------------------------------------------------------
# SSLContext(Configurable) configuration
#------------------------------------------------------------------------------

## SSL CA, use with keyfile and certfile
#c.SSLContext.cafile = ''

## SSL cert, use with keyfile
#c.SSLContext.certfile = ''

## SSL key, use with certfile
#c.SSLContext.keyfile = ''

