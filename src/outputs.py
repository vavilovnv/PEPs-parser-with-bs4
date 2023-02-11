import logging
import csv
import datetime as dt

from argparse import Namespace
from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def control_output(results: list, cli_args: Namespace) -> None:
    """
    Обработка формата вывода данных: обычный вывод в консоль, в консоль в виде
    pretty-table или в csv-файлы.
    """
    output = cli_args.output
    if output == 'pretty':
        pretty_output(results)
    elif output == 'file':
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results: list) -> None:
    """
    Вывод данных в консоль.
    """
    for row in results:
        print(*row)


def pretty_output(results: list) -> None:
    """
    Вывод данных в консоль в формате pretty-table.
    """
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results: list, cli_args: Namespace) -> None:
    """
    Вывод данных в формате csv-файла.
    """
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='UTF-8') as f:
        writer = csv.writer(f, dialect='unix')
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранен: {file_path}')
