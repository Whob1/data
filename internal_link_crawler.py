import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from session_manager import create_session
from scrape_manager import get_internal_links

logging.basicConfig(level=logging.INFO)

def crawl_internal_links(domain): 
    visited = set()
    session = create_session()
    urls_to_visit = set([domain])  # Starting with the base domain
    all_page_contents = {}

    while urls_to_visit:
        current_url = urls_to_visit.pop()
        if current_url in visited:
            continue

        try:
            response = session.get(current_url)
            if response.status_code == 200:
                logging.info(f'Successfully fetched content from {current_url}')
                soup = BeautifulSoup(response.text, 'html.parser')
                all_page_contents[current_url] = soup
                for link in get_internal_links(get_domain(current_url), soup):
                    if link not in visited:
                        urls_to_visit.add(link)
            else:
                logging.error(f'Failed to fetch {current_url}: Status code {response.status_code}')
        except Exception as e:
            logging.error(f'Exception fetching {current_url}: {e}', exc_info=True)

        visited.add(current_url)

    return all_page_contents

