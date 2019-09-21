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

