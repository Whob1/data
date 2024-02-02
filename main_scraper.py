import requests
from bs4 import BeautifulSoup
import logging

from domain_list import load_approved_domains  
from content_parser import extract_data_from_html
from data_cleaner import process_extracted_data
from csv_exporter import export_data_to_csv
from concurrent.futures import ThreadPoolExecutor
from data_cleaner import process_extracted_data
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)

def extract_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all text from the page
    text = ' '.join(tag.get_text() for tag in soup.find_all(True))

    # Clean the text
    text = text.replace('\n', ' ').replace('\r', '').strip()

    return text
def crawl_internal_links(domain, soup):
    links = []
    for link in soup.find_all('a'):
        url = link.get('href')
        if url:
            if url.startswith(('http:', 'https:')):
                if url.startswith(domain):
                    links.append(url)
            else:
                # Join the domain with the relative URL
                absolute_url = urljoin(domain, url)
                if absolute_url.startswith(domain):
                    links.append(absolute_url)
    return links

from bs4 import BeautifulSoup

def fetch_page(url):
  try:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract all text from the page
    text = ' '.join(tag.get_text() for tag in soup.find_all(True))

    # Clean the text
    text = text.replace('\n', ' ').replace('\r', '').strip()

    return text
  except Exception as e:
    logging.error(f"Error fetching page {url}: {e}", exc_info=True)

def fetch_pages(urls):
  with ThreadPoolExecutor(max_workers=10) as executor:
    return list(executor.map(fetch_page, urls))

  def extract_data(soup):
    return {'text': ' '.join([p.text for p in soup.find_all('p')])}

def scrape_domain(domain, visited=None, all_data=None):
    if visited is None:
        visited = set()
    if all_data is None:
        all_data = []

    if domain not in visited:
        visited.add(domain)

        try:
            response = requests.get(domain)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract and clean data from the current page
            raw_data = extract_data(soup)
            cleaned_data = process_extracted_data(raw_data)  # Use process_extracted_data instead of clean_data

            result = {
                'url': domain,
                'data': cleaned_data
            }
            all_data.append(result)

            # Find all internal links on the current page
            for link in soup.find_all('a', href=True):
                url = urljoin(domain, link['href'])
                if url.startswith(domain) and url not in visited:
                    # Recursively scrape the linked page
                    scrape_domain(url, visited, all_data)
        except Exception as e:
            logging.error(f'Error scraping {domain}: {e}')

    return all_data

def main():
  domains = load_approved_domains()
  all_results = []
  for domain in domains:
    logging.info(f'Scraping domain: {domain}')
    results = scrape_domain(domain)
    if results:
      all_results.extend(results)
  export_data_to_csv(all_results, 'results.csv')

if __name__ == '__main__':
  main()