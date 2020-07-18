import logging
from bot import app


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())

    # Uncomment this line to log request information.
    # logger.setLevel(logging.DEBUG)

    app.app.run(port=3000)
