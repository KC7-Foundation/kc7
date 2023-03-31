import os

# to set vars automatically in dev
# source ./set_config.py 


# in production check this out
# https://devcenter.heroku.com/articles/config-vars#managing-config-vars

class BaseConfig(object):
    DEBUG = False
    TESTING = False
    
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE_CONNECT_OPTIONS = {}

    # Application threads. A common general assumption is
    # using 2 per available processor cores - to handle
    # incoming requests using one and performing background
    # operations using the other.
    THREADS_PER_PAGE = 2

    SQLALCHEMY_DATABASE_URI = 'sqlite:///flaskr.db'
    
    # Secret key for signing cookie. You should replace this
    SECRET_KEY = 'y?,???\???Z#?N'

    ################################
    # AZURE ENVIRONMENT VARIABLES
    # FOLLOW THE README TO REPLACE THESE VALUES
    ################################

    AAD_TENANT_ID = "{YOUR TENANT ID}" #https://docs.microsoft.com/en-us/azure/active-directory/fundamentals/active-directory-how-to-find-tenant
    KUSTO_URI = "https://{clustername}.eastus.kusto.windows.net"
    KUSTO_INGEST_URI =  "https://ingest-{clustername}.eastus.kusto.windows.net"
    DATABASE = "SecurityLogs"

    # Register an azure application and generate secrets
    # give the app permission to edit your azure data explorer cluster
    # App secret can only be seen right after creation
    CLIENT_ID = "{YOUR REGISTERED APP CLIENT ID}" 
    CLIENT_SECRET = "{YOUR RESTERED APP CLIENT SECRET}"
    

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True

    ADX_DEBUG_MODE=True   # Set to True if you don't want to write to Azure

    SQLALCHEMY_DATABASE_URI = 'sqlite:///flaskr.db'


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True

    
class ProductionConfig(BaseConfig):
    DEBUG = False
    #SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_HERE']

class ActivityVolumeSettings(BaseConfig):
    ACTOR_SKIPS_DAY_RATE = 0.1
    RATE_USER_AUTHS_FROM_WORK = 0.7

    RATE_DOMAIN_RESOLVES_TO_NEW_IP = 0.2
    RATE_USER_BROWSE_TO_PARTNER_DOMAIN_RANDOM = 0.05
    RATE_USER_BROWSE_TO_RANDOMIZED_DOMAIN = 0.35
    RATE_USER_BROWSE_TO_LEGIT_DOMAIN = 0.60

    # Set up your NewsAPI and YouTubeAPI keys here. 
    # NewsAPI (Free): https://newsapi.org/docs/get-started
    # Youtube Data API v3 (Free):  https://console.developers.google.com/
    API_NEWSAPI = "apikey"
    API_YOUTUBEAPI = "apikey"

    FP_RATE_EMAIL_ALERTS = 0.1
    TP_RATE_EMAIL_ALERTS = 0.2

    TP_RATE_HOST_ALERTS = 0.1
    FP_RATE_HOST_ALERTS = 0.001

    RATE_ACTOR_SKIPS_HANDS_ON_KEYBOARD = 0.1