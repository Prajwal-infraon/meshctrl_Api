import logging
import os
from logging.handlers import RotatingFileHandler
def configure_loggers():
    logs_dir = 'logs'

    # Create logs directory if it doesn't exist
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Logger for general messages
    app_logger = logging.getLogger('Mesh Central')
    app_logger.setLevel(logging.DEBUG)

    app_handler = RotatingFileHandler(os.path.join(logs_dir,'app.log'), 'a', maxBytes=1024 * 1024 * 50, backupCount=5)
    app_formatter = logging.Formatter(fmt = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s', datefmt = '%Y-%m-%dT%H:%M:%S%z')
    app_handler.setFormatter(app_formatter)

    app_logger.addHandler(app_handler)

    # Logger for error messages
    mongo_logger = logging.getLogger('Mongo DB')
    mongo_logger.setLevel(logging.INFO)

    mongo_handler = RotatingFileHandler(os.path.join(logs_dir,'mongo.log'))
    mongo_formatter = logging.Formatter(fmt = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s', datefmt = '%Y-%m-%dT%H:%M:%S%z')
    mongo_handler.setFormatter(mongo_formatter)

    mongo_logger.addHandler(mongo_handler)

    return app_logger, mongo_logger
