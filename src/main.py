import logging
import re
from urllib.parse import urljoin

import requests_cache

from bs4 import BeautifulSoup
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEPS_URL
from exceptions import ParserFindTagException
from outputs import control_output
from utils import get_pep_status, get_response, find_tag


def whats_new(session: CachedSession) -> list[tuple] | None:
    """
    Парсинг страниц с описанием обновлений в версиях Python.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    logging.info('Parsing news started')
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(
        main_div,
        'div',
        attrs={'class': 'toctree-wrapper'}
    )
    section_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(section_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = soup.find(name='dl')
        result.append((
            version_link,
            h1.text.strip().replace('\n', ' '),
            dl.text.strip().replace('\n', ' ')
        ))
    logging.info('Parsing news finished')
    return result


def latest_versions(session):
    """
    Парсинг информации по актуальным версиям Python.
    """
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    logging.info('Getting latest version started')
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = soup.find(name='div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all(name='ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException('Found nothing')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in tqdm(a_tags):
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append((link, version, status))
    logging.info('Getting latest version finished')
    return results


def download(session):
    """
    Скачивание zip-архива с документацией актуальной версии Python.
    """
    download_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, download_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    table_tag = soup.find(name='table', attrs={'class': 'docutils'})
    pdf_a4_tag = table_tag.find(
        name='a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(download_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as f:
        f.write(response.content)
    logging.info(f'Архив был загружен и сохранен: {archive_path}')


def pep(session):
    """
    Парсинг информации по статусам Python Enhancement Proposals.
    """
    response = get_response(session, PEPS_URL)
    if response is None:
        return
    logging.info('Parsing PEP statuses started')
    results, warnings = [], []
    soup = BeautifulSoup(response.text, features='lxml')
    section_div = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tr_divs = BeautifulSoup.find_all(section_div, 'tr')
    for tr_div in tqdm(tr_divs[1:]):
        abbr_div = find_tag(tr_div, 'abbr')
        short_status = abbr_div.text[1:]
        a_div = find_tag(
            tr_div,
            'a',
            attrs={'class': 'pep reference internal'}
        )
        short_url = a_div.attrs.get('href', '')
        url = urljoin(PEPS_URL, short_url)
        status = get_pep_status(session, url)
        results.append((status, short_status, url))
        if short_status and status not in EXPECTED_STATUS[short_status]:
            warnings.append((status, short_status, url))
    if warnings:
        logging.warning('Несовпадающие статусы:')
        for warning in warnings:
            logging.warning(
                '%s\nСтатус в карточке: %s\nОжидаемые статусы: %s',
                warning[2],
                warning[0],
                list(EXPECTED_STATUS[warning[1]])
            )
    logging.info('Parsing PEP statuses finished')
    if not results:
        return None
    result = [('Статус', 'Количество')]
    for status in set([i[0] for i in results]):
        data = [s for s in results if s[0] == status]
        result.append((f'Количество PEP в статусе {status}', len(data)))
    result.append(('Общее количество PEP', len(results)))
    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Parser started')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info('command line arguments: %s', args)
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    func = MODE_TO_FUNCTION[parser_mode]
    results = func(session)
    if results is not None:
        control_output(results, args)
    logging.info('All jobs done')


if __name__ == '__main__':
    main()
