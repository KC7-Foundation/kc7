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
    
    # Secret key for signing cookies
    SECRET_KEY = 'FLASK_SECRET_KEY'

    # Azure log analystics credentials
    CUSTOMER_ID = 'CUSTOMER_ID'
    SHARED_KEY = "SHARED_KEY"

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True

    LOG_PREFIX = 'TEST10'
    DEBUG_MODE=True   #Set to True if you don't want to write to Azure

    SQLALCHEMY_DATABASE_URI = 'sqlite:///flaskr.db'


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True

    
class ProductionConfig(BaseConfig):
    DEBUG = False
    #SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL_HERE']
    
    