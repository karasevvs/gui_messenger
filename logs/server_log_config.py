import logging
from logging import handlers
import sys
import os
import common.variables as variables

LOG_DIRECTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), variables.LOG_DIRECTORY)
LOG_FILE_PATH = os.path.join(LOG_DIRECTORY_PATH, variables.LOG_FILENAME_SERVER)

LOGGER = logging.getLogger('server')
LOGGER.setLevel(logging.DEBUG)

FORMAT = logging.Formatter('%(asctime)-20s %(levelname)-8s %(filename)-10s %(message)s')

STDERR_HANDLER = logging.StreamHandler(sys.stderr)
STDERR_HANDLER.setLevel(logging.INFO)
STDERR_HANDLER.setFormatter(FORMAT)

FILE_HANDLER = handlers.TimedRotatingFileHandler(LOG_FILE_PATH, 'D', 1, encoding='utf-8')
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMAT)

LOGGER.addHandler(STDERR_HANDLER)
LOGGER.addHandler(FILE_HANDLER)

LOGGER_FUNC = logging.getLogger('server_func')
LOGGER_FUNC.setLevel(logging.DEBUG)
FILE_HANDLER_FUNC = logging.FileHandler(os.path.join(LOG_DIRECTORY_PATH, 'server_func.log'))
FILE_HANDLER_FUNC.setLevel(logging.DEBUG)
FILE_HANDLER_FUNC.setFormatter(FORMAT)
LOGGER_FUNC.addHandler(FILE_HANDLER_FUNC)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
    LOGGER.warning('Внимание')
