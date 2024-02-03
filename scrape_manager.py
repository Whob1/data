from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from session_manager import create_session
from nlp_setup import initialize_nlp
import time

session = create_session()
nlp, sia = initialize_nlp()

def get_domain(url):
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

def scrape_page(url):
    response = session.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.text.strip() if soup.title else None
    body = ' '.join([p.text for p in soup.find_all('p')])
    keyword_data = []  # Placeholder for keyword extraction
    return {
        "title": title,
        "body": body,
        "keywords": keyword_data,
        "url": url,
        "domain": get_domain(url)
    }

def get_internal_links(soup):
  links = []
  for link in soup.find_all('a', href=True): 
    links.append(link['href'])
  return links