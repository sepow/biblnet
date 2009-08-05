# -*- coding: utf-8 -*-
# Django settings for complete pinax project.

import os.path
import pinax

PINAX_ROOT = os.path.abspath(os.path.dirname(pinax.__file__))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# tells Pinax to use the default theme
PINAX_THEME = 'default'

TIME_FORMAT = 'H:i'
DEFAULT_MAX_COMMENT_LENGTH = 15000
DEFAULT_CHARSET = "utf-8"
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# tells Pinax to serve media through django.views.static.serve.
SERVE_MEDIA = True

AUTHENTICATION_BACKENDS = (
    'sepow.profilestuff.CaseInsensitiveModelBackend',
)


ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'    # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_NAME = 'dev.db'       # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Copenhagen'
DATETIME_FORMAT = 'N j, Y, H:i'
# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), "media")

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'bk-e2zv3humar79nm=j*bwc=-ymeit(8a20whp3goq4dh71t)s'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'dbtemplates.loader.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django_openid.consumer.SessionConsumer',
    'account.middleware.LocaleMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'misc.middleware.SortOrderMiddleware',
    'djangodblog.middleware.DBLogMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    #'sepow.middleware.UserBasedExceptionMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'biblnet.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
    os.path.join(PINAX_ROOT, "templates", PINAX_THEME),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    
    "notification.context_processors.notification",
    "announcements.context_processors.site_wide_announcements",
#    "account.context_processors.openid",
    "account.context_processors.account",
    "misc.context_processors.contact_email",
    "misc.context_processors.site_name",
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "misc.context_processors.combined_inbox_count",
    "sepow.context_processors.affil_tribe",
    
)

COMBINED_INBOX_COUNT_SOURCES = (
    "messages.context_processors.inbox",
    "friends_app.context_processors.invitations",
    "notification.context_processors.notification",
)

# Search 

HAYSTACK_SEARCH_ENGINE = 'whoosh'
HAYSTACK_WHOOSH_PATH = os.path.join(os.path.dirname(__file__), 'biblnet_index')

INSTALLED_APPS = (
    # included
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.markup',
    
    # external
    'notification', # must be first
    #'django_openid',
    'emailconfirmation',
    'django_extensions',
    'robots',
    'dbtemplates',
    'friends',
    'mailer',
    'messages',
    'announcements',
    'oembed',
    'djangodblog', # remove?
    'pagination',
#    'gravatar',
    'threadedcomments',
    'wiki',
    'swaps', # remove
    'timezones',
    'app_plugins',
    'voting', 
    'tagging',
    'bookmarks', 
    'blog', # remove?
    'ajax_validation',
    'photologue',
    'avatar',
    'flag',
    'microblogging',
    'locations', # remove
    'uni_form',
    
    # internal (for now)
    'analytics',
    'profiles',
    'staticfiles',
    'account',
    'tribes',
    'projects', # remove
    'misc',
    'photos',
    'tag_app',
    'debug_toolbar',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'sepow',
    'captcha',
    'markitup',
    'haystack',
    'django_dms',
    'django_dms.apps.small_dms',
    'sorl.thumbnail',
    'schedule',
    'elsewhere',
    'compressor',
    'django_extensions',
#    'south',
)

# Import sorl.thumbnail if it is available
try:
    import sorl.thumbnail
    INSTALLED_APPS += ('sorl.thumbnail',)
except ImportError:
    pass

DEBUG_TOOLBAR_CONFIG = { 'INTERCEPT_REDIRECTS' : False, } 

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/%s/" % o.username,
}

AUTH_PROFILE_MODULE = 'profiles.Profile'

NOTIFICATION_LANGUAGE_MODULE = 'account.Account'

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG
CONTACT_EMAIL = "test@example.com"
SITE_NAME = "Biblnet"
LOGIN_URL = "/account/login"
LOGIN_REDIRECT_URLNAME = "home"

INTERNAL_IPS = (
    '127.0.0.1',
)

ugettext = lambda s: s
LANGUAGES = (
  ('da', u'Danish'),
  ('en', u'English'),
)

# URCHIN_ID = "ua-..."

# CHACHE STUFF

CACHE_BACKEND = "dummy:///?max_entries=300"

COMPRESS_CSS_FILTERS = ('compressor.filters.css_default.CssAbsoluteFilter',)

FEEDUTIL_SUMMARY_LEN = 60*7 # 7 hours

class NullStream(object):
    def write(*args, **kw):
        pass
    writeline = write
    writelines = write

RESTRUCTUREDTEXT_FILTER_SETTINGS = { 'cloak_email_addresses': True,
                                     'file_insertion_enabled': False,
                                     'raw_enabled': False,
                                     'warning_stream': NullStream(),
                                     'strip_comments': True,}

# if Django is running behind a proxy, we need to do things like use
# HTTP_X_FORWARDED_FOR instead of REMOTE_ADDR. This setting is used
# to inform apps of this fact
BEHIND_PROXY = False

FORCE_LOWERCASE_TAGS = True

WIKI_REQUIRES_LOGIN = True

AVATAR_DEFAULT_URL = MEDIA_URL + 'images/kristine.jpg'
AVATAR_GRAVATAR_BACKUP = False

# Schedule - calendar

FIRST_DAY_OF_WEEK = 1 # Monday

def check_edit_permission(ob, user):
    if not ob: # opret
        return user.is_authenticated()    
   
    #edit v 
    tribe = ob.calendar.calendarrelation_set.all()[0].content_object
    from tribes.models import TribeMember
    if user.is_authenticated():
        if TribeMember.objects.filter(tribe=tribe, user=user).count() > 0:
            return True
    return False
    
CHECK_PERMISSION_FUNC = check_edit_permission



# Captcha

CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge' 
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)

# local_settings.py can be used to override environment-specific settings
# like database and email that differ between development and production.
try:
    from local_settings import *
except ImportError:
    pass
    

