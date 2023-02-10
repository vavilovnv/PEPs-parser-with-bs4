import logging
from logging.handlers import RotatingFileHandler

import argparse

from constants import BASE_DIR


LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


def configure_argument_parser(aviable_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=aviable_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кэша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotating_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 ** 6,
        backupCount=5
    )

    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
