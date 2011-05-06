#!/usr/bin/env python
import httplib
import logging
import os

from consts import CRLF, PROTOCOL
from options import enable_pretty_logging
enable_pretty_logging()

PWD = os.path.dirname(os.path.realpath(__file__))


def _logger(level = logging.DEBUG,
           output_to_stdout = False,
           path = os.path.join(PWD, "log", '%d.log' % logging.DEBUG)):

    logger = logging.getLogger()
    logger.setLevel(level)

    # save log into  static file
    if path:
        file_ch = logging.FileHandler(filename = path)
        file_ch.setLevel(level)
        formatter = logging.Formatter("[%(levelname)s] [%(asctime)s]"
                                      " [%(name)s] %(message)s")
        file_ch.setFormatter(formatter)
        logger.addHandler(file_ch)

    # print log to stdout/stderr
    if output_to_stdout:
        stream_ch = logging.StreamHandler()
        stream_ch.setLevel(level)
        formatter = logging.Formatter("[%(levelname)s] [%(asctime)s]"
                                      " [%(name)s] %(message)s")
        stream_ch.setFormatter(formatter)
        logger.addHandler(stream_ch)

    return logger
logger = _logger(path = None)


def error(*args, **kwargs):
    logger.error(*args, **kwargs)


def smart_log(*args, **kwargs):
    if not kwargs and len(args) == 1:
        arg = args[0]
        if isinstance(arg, str) or isinstance(arg, unicode):
            first_line = arg.split(CRLF)[0]

            pos = first_line.find(PROTOCOL) + len("%s " % PROTOCOL)
            CODE_NOT_FOUND = pos >= len(first_line)
            if CODE_NOT_FOUND:
                logger.debug(*args, **kwargs)
                return

            code = first_line[pos : (pos + 3)]

            try:
                code = int(code)
                if code == httplib.OK:
                    logger.info(*args, **kwargs)
                else:
                    error(*args, **kwargs)
            except ValueError:
                logger.debug(*args, **kwargs)
    else:
        logger.debug(*args, **kwargs)


if __name__ == '__main__':
    logger.debug("debug message")
    logger.info("info message")
    logger.warn("warn message")
    logger.error("error message")
    #log.critical("critical message")
    logger.error(u'hello')

    for i in ('SIP-C/4.0 200 OK', 'R fetion.com.cn SIP-C/4.0'):
        smart_log(i)

