import csv
import datetime as dt
import logging
from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    results_dir = BASE_DIR / 'results'
    try:
        results_dir.mkdir(exist_ok=True)
        file_path = results_dir / file_name
        with open(file_path, 'w', encoding='utf-8') as f:
            writer = csv.writer(f, dialect='unix')
            writer.writerows(results)
    except PermissionError:
        logging.exception(
            f'Недостаточно прав для создания файлов в {BASE_DIR}',
            exc_info=True
            )
        raise
    except OSError:
        logging.exception(
            f'Ошибка при работе с файлами в {BASE_DIR}',
            exc_info=True
            )
        raise
    logging.info(f'Файл с результатами был сохранён: {file_path}')
