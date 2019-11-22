DB_USER = 'root'
DB_PASS = 'root'
DB_NAME = 'forums_djago2_1'
PUB_KEY = 'Public Key'
PRIV_KEY = 'Private Key'
TO_EMAIL_ID = 'prashant@fossee.in'
SET_SITE_ID = 2

SITE_DEBUG = False #set debug option

SENDER_EMAIL = 'no-reply@fossee.in'
FORUM_NOTIFICATION = 'forum-notifications@fossee.in'
BCC_EMAIL_ID = 'web-team@fossee.in'
EMAIL_URL = 'https://forums.fossee.in'

DOMAIN_NAME = 'https://forums.fossee.in'
# Host for sending e-mail.
EMAIL_HOST_SERVER = 'localhost'

# Port for sending e-mail.
EMAIL_PORT_SERVER = 25

# Optional SMTP authentication information for EMAIL_HOST.
#EMAIL_HOST_USER_SERVER = 'email host user'
#EMAIL_HOST_PASSWORD_SERVER = 'email host user password'
#EMAIL_USE_TLS_SERVER = 'Use TLS'


ADMINS_EMAIL_ADDRESS = [('prashant','prashant@fossee.in'), ('Sysads', 'sysads@fossee.in')] #[('name', 'id@email.id')]

SERVER_EMAIL_ADDRESS = 'webmaster@fossee.in'


FORUM_GOOGLE_RECAPTCHA_SECRET_KEY = '6LfjLEUUAAAAACWfHEhE4-PD2ALTTjUiHMoQ28wT'
FORUM_GOOGLE_RECAPTCHA_SITE_KEY = '6LfjLEUUAAAAAJJo4QuG0Ewb3bnHDoOQ6r5805-I'
#FORUM_GOOGLE_RECAPTCHA_SECRET_KEY = '6LfhIhsTAAAAABQ_Qcyh82hpXKoyt07578m1CCoH'
#FORUM_GOOGLE_RECAPTCHA_SITE_KEY = '6LfhIhsTAAAAANIJZWgN6oCYMGQpRbZTfXmVIkbL'


#Train spamfilter(default set as True)
TRAIN_SPAMFILTER = True

#ALLOWED_HOSTS
SYSTEM_ALLOWED_HOSTS = ['127.0.0.1']

#Secre key for application (any random 32 alphanumeric characters)
SECRET_KEY_CODE = 'LRkw0qob4PsTSuEGVktSzevmkEDYDpAvFuVe+dit8FQ='



# Maximum file size in MB
MAX_FILE_SIZE_MB = 2
