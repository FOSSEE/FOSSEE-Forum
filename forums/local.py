DB_USER = 'root'
DB_PASS = 'root'
DB_NAME = 'forums_djago2_1'
PUB_KEY = 'Public Key'
PRIV_KEY = 'Private Key'
TO_EMAIL_ID = 'to@email.id'
SET_SITE_ID = 2

SITE_DEBUG = ['False'] #set debug option

SENDER_EMAIL = 'sender@mail.com'
BCC_EMAIL_ID = 'bcc@mail.com'
FORUM_NOTIFICATION = 'forumnotifications@email.id'

EMAIL_URL = 'Site URL for email content'

DOMAIN_NAME = '#http://domain.name'
# Host for sending e-mail.
EMAIL_HOST_SERVER = 'localhost'

# Port for sending e-mail.
EMAIL_PORT_SERVER = 25

# Optional SMTP authentication information for EMAIL_HOST.
#EMAIL_HOST_USER_SERVER = 'email host user'
#EMAIL_HOST_PASSWORD_SERVER = 'email host user password'
#EMAIL_USE_TLS_SERVER = 'Use TLS'


ADMINS_EMAIL_ADDRESS = '[Admins mail address]' #[('name', 'id@email.id'), ('name', 'id@email.id')]

SERVER_EMAIL_ADDRESS = 'server email address'


FORUM_GOOGLE_RECAPTCHA_SECRET_KEY = 'google recaptcha secret key'
FORUM_GOOGLE_RECAPTCHA_SITE_KEY = 'google recaptcha site key'

#Train spamfilter(default set as True)
TRAIN_SPAMFILTER = True

#ALLOWED_HOSTS
SYSTEM_ALLOWED_HOSTS = ['Enter the host name' ]

#Secre key for application (any random 32 alphanumeric characters)
SECRET_KEY_CODE = 'any random 32 alphanumeric characters'

# Maximum file size in MB
MAX_FILE_SIZE_MB = 2
