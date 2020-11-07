# -*- coding: utf-8 -*-
import logging


def get_logger(logger_name, log_name, level=logging.INFO):
    l = logging.getLogger(logger_name)
    l.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s %(filename)s [line:%(lineno)d] %(message)s',
                                  "%Y-%m-%d %H:%M:%S")
    info_file_handler = logging.FileHandler('{}_info.log'.format(log_name), mode='a')
    info_file_handler.setFormatter(formatter)
    info_file_handler.setLevel(level)

    error_file_handler = logging.FileHandler('{}_error.log'.format(log_name), mode='a')
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    for handler in (info_file_handler, error_file_handler, console_handler):
        l.addHandler(handler)
    return l


logger = get_logger('sql_simulation', 'sql_simulation')
