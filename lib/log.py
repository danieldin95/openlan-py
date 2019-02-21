'''
Created on Feb 21, 2019

@author: Daniel
'''

import logging

isConfig = False

def basicConfig(filename='openlan.log', level=logging.DEBUG):
    """
    logging.debug("This is a debug log.")
    logging.info("This is a info log.")
    logging.warning("This is a warning log.")
    logging.error("This is a error log.")
    logging.critical("This is a critical log.")
    """
    global isConfg

    if isConfig:
        return

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename = filename, level = level, format = LOG_FORMAT)
