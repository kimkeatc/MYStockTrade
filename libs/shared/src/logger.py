#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Import standard libraries
import logging
import sys

def get_logger(name: str|None = None, level=logging.DEBUG, fmt: str = "[%(asctime)s] [%(levelname)8s] [%(pathname)s] - #L%(lineno)03d : %(message)s", datefmt: str = "%y/%m/%d %H:%M:%S"):

    logger = logging.getLogger(name=name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(level=level)

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(fmt=logging.Formatter(fmt=fmt, datefmt=datefmt))
    logger.addHandler(hdlr=stream_handler)
    return logger
