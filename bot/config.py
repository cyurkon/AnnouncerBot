from os import environ, getcwd


class Config:
    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")


class DevConfig(Config):
    # Database
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + getcwd() + "/tribeB.db"
