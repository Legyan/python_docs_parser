import re
import logging
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_URL
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
        )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    for tag in a_tags:
        link = (tag['href'])
        text_match = re.search(pattern, tag.text)
        if text_match:
            version, status = text_match.group('version', 'status')
            results.append((link, version, status))
        else:
            results.append((link, tag.text, ''))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    table = find_tag(soup, 'table', {'class': 'docutils'})
    pattern = r'.+pdf-a4\.zip$'
    pdf_a4_tag = find_tag(table, 'a', {'href': re.compile(pattern)})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    archive_response = session.get(archive_url)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    try:
        downloads_dir.mkdir(exist_ok=True)
        archive_path = downloads_dir / filename
        with open(archive_path, 'wb') as file:
            file.write(archive_response.content)
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
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEPS_URL)
    if response is None:
        return
    peps_soup = BeautifulSoup(response.text, 'lxml')
    section = find_tag(
        peps_soup, 'section', attrs={'id': 'numerical-index'}
    )
    table = find_tag(section, 'tbody')
    preset_statuses = []
    for tuple_of_statuses in EXPECTED_STATUS.values():
        for status in tuple_of_statuses:
            preset_statuses.append(status)
    pep_counts = {
        status: zero
        for (status, zero) in zip(preset_statuses, [0] * len(preset_statuses))
        }
    total_count = 0
    table_statuses_tags = table.find_all('abbr')
    table_statuses = [
        status_tag.text[1:] for status_tag in table_statuses_tags
        ]
    if not table_statuses:
        table_statuses.append('')
    pattern = r'^\d+$'
    table_links_tags = table.find_all('a', text=re.compile(pattern))
    for link_tag, preview_status in zip(table_links_tags, table_statuses):
        pep_link = PEPS_URL + link_tag['href']
        response = get_response(session, pep_link)
        if response is None:
            return
        pep_soup = BeautifulSoup(response.text, 'lxml')
        pep_status = find_tag(pep_soup, 'abbr').text
        if pep_status not in EXPECTED_STATUS[preview_status]:
            mismatch_status_message = (
                f'Несовпадающие статусы:\n'
                f'{pep_link}\n'
                f'Статус в карточке: {pep_status}\n'
                f'Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}')
            logging.info(mismatch_status_message)
        if pep_status not in pep_counts:
            pep_counts[pep_status] = 0
        pep_counts[pep_status] += 1
        total_count += 1
    fields_names = [('Статус', 'Количество')]
    results = (
        fields_names +
        list(pep_counts.items()) +
        [('Total', total_count)]
        )
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
