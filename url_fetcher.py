import requests
from requests.exceptions import RequestException 
import logging
from session_manager import create_session
from domain_list import load_approved_domains
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

def crawl_internal_links(domain, soup):
  links = []
  
  for link in soup.find_all('a'):
    url = link.get('href')
    if url.startswith('/'):
      links.append(domain + url)

  return links

def fetch_html_content(domain_list):
  session = create_session()
  results = {}

  for domain in domain_list:
    try:
      response = session.get(domain)
      if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        results[domain] = crawl_internal_links(domain, soup)
        logging.info(f'Successfully initiated crawling for {domain}')  
      else:
        logging.error(f'Failed to fetch {domain}: Status code {response.status_code}')
        results[domain] = f'Failed to fetch: Status code {response.status_code}'
    except RequestException as e:
      logging.error(f'Failed to fetch {domain}: {e}', exc_info=True)
      results[domain] = f'Failed to fetch: {e}' 
    except Exception as e:
      logging.error(f'An error occurred during fetching or crawling for {domain}: {e}', exc_info=True)
      results[domain] = f'An error occurred: {e}'
  
  return results

if __name__ == '__main__':
  try:
    approved_domains = load_approved_domains()
    results = fetch_html_content(approved_domains)
    
    for domain, content in results.items():
      if isinstance(content, dict):
        logging.info(f'{domain}: Crawling completed with {len(content)} pages fetched')
      else:
        logging.info(f'{domain}: {content}')
        
  except Exception as e:
    logging.error(f'An error occurred in URL fetching module: {e}', exc_info=True)