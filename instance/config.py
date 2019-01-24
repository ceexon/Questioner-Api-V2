""" API config File """
import os


class Config(object):
    """ Parent configuration class """

    DEBUG = False
    TESTING = False
    Database_Url = os.getenv("Main_Database")
    SECRET_KEY = os.getenv("SECRET")


class DevelopmentConfig(Config):
    """ Configuration for development environment """
    DEBUG = True
    Database_Url = os.getenv("Main_Database")


class StagingConfig(Config):
    """ Configuration for the staging environment """
    DEBUG = True
    Database_Url = os.getenv("Test_Database")


class TestingConfig(Config):
    """ Configuration for the testing environment """
    TESTING = True
    DEBUG = True
    Database_Url = os.getenv("Test_Database")


class ProductionConfig(Config):
    """ Configuration for the production environment """
    DEBUG = False
    TESTING = False
    Database_Url = os.getenv("DATABASE_URL")


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}
