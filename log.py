# !/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
from threading import local

from config import LOG_FORMAT, LOG_LEVEL

_local = local()
_local.loggers = dict()
_local.log_file_path = None


def reset_log_path(log_file_path):
    _local.log_file_path = log_file_path
    _local.loggers.clear()


def create_logger(logger_name):
    # set log level
    logger = logging.getLogger(logger_name)
    logger.setLevel(level=LOG_LEVEL)

    # set log format
    formatter = logging.Formatter(LOG_FORMAT)

    # add console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # add file handler
    if _local.log_file_path:
        file_handler = logging.FileHandler(_local.log_file_path)
        file_handler.setLevel(logging.WARN)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # save handler
    _local.loggers[logger_name] = logger

    return logger


def get_logger(logger_name=None):
    # return the corresponding logger if present
    if logger_name in _local.loggers:
        return _local.loggers[logger_name]

    return create_logger(logger_name)
