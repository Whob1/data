import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
import spacy
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from memory_profiler import profile
import csv  # Added import for CSV handling
import concurrent.futures  # Added import for ThreadPoolExecutor

# Logging setup
logging.basicConfig(level=logging.INFO)

# session_manager.py
def create_session():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

# nlp_setup.py
def initialize_nlp():
    nlp = spacy.load("en_core_web_sm")
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()
    return nlp, sia

# data_cleaner.py

@profile
def clean_text(dict_data):
    text = dict_data.get('text', '')  # Extract the text from the dictionary
    cleaned_text = text.replace('\n', ' ').replace('\r', '').strip()
    return cleaned_text

def extract_keywords(cleaned_text):
    extracted_data = {}
    for keyword, pattern in keyword_patterns.items():
        match = re.search(pattern, cleaned_text, re.IGNORECASE)
        if match:
            extracted_data[keyword] = match.group(1).strip()
    return extracted_data

def chunks(lst, chunk_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

def process_url(url):
    """Process a single URL and return the data"""
    try:
        return scrape_page(url)
    except Exception as e:
        logging.error(f"Error processing URL {url}: {e}", exc_info=True)
        return None

# csv_exporter.py
def export_data_to_csv(data, filename):
    try:
        df = pd.DataFrame(data)
        if 'keywords' in df.columns:
            df['keywords'] = df['keywords'].apply(lambda x: ', '.join([f'{k}: {v}' for k, v in x.items()]))
        df.to_csv(filename, index=False)
        logging.info('Data successfully exported to CSV')
    except Exception as e:
        logging.error(f"Error exporting data to CSV: {e}", exc_info=True)

# Added function to extract harm reduction info and write to CSV
def extract_harm_reduction_info(text, domain):
    """Extract harm reduction information from text"""
    keywords = ['dose', 'substances', 'peak', 'onset', 'duration', 'adverse effects', 'interactions']
    data = {}  # Dictionary to store extracted information

    for keyword in keywords:
        matches = re.findall(rf'{keyword}\s*:\s*([\w\.%]+)', text, flags=re.IGNORECASE)  # Adjusted regex
        if matches:
            data[keyword] = '; '.join(matches)  # Join multiple matches with semicolon delimiter
    data['Domain'] = domain  # Add domain name to the extracted data
    return data

def write_data_to_csv(filename, data):
    """Write scraped data to a CSV file"""
    try:
        with open(filename, 'w', newline='') as f:
            fieldnames = ['Domain'] + list(next(iter(data.values())).keys())  # Get header row from the first dictionary value
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()  # Write header row
            for domain, info in data.items():
                row_data = {'Domain': domain}
                row_data.update(info)  # Update row data with extracted information
                writer.writerow(row_data)
            
            print("Row data before writing to CSV:", row_data)
    except Exception as e:
        logging.error("Error occurred while writing scraped data to CSV file: %s", filename, exc_info=True)
        print(f"Error occurred while writing scraped data to CSV file: {filename}\nError details: {e}")

# scrape_manager.py
session = create_session()
nlp, sia = initialize_nlp()

def get_domain(url):
    parsed_uri = urlparse(url)
    return '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

@profile
def scrape_page(url):
    response = session.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.text.strip() if soup.title else None
    body = ' '.join([p.text for p in soup.find_all('p')])
    cleaned_text = clean_text({'text': body})
    keyword_data = extract_keywords(cleaned_text)
    
    # Extract harm reduction information and update keyword_data
    harm_reduction_info = extract_harm_reduction_info(cleaned_text, get_domain(url))
    keyword_data.update(harm_reduction_info)
    
    return {
        "title": title,
        "body": body,
        "keywords": keyword_data,
        "url": url,
        "domain": get_domain(url)
    }

@profile
def get_internal_links(domain, soup):
    internal = set()
    for link in soup.find_all('a', href=True):
        href = urljoin(domain, link['href']).rstrip('/')
        if href.startswith(domain):
            internal.add(href)
    return internal

@profile
def crawl_domain(domain):
    visited = set()
    urls_to_visit = {domain}
    all_data = []

    chunk_size = 10  # Adjust the chunk size based on your preference
    url_chunks = list(chunks(list(urls_to_visit), chunk_size))

    for i, chunk in enumerate(url_chunks, start=1):
        chunk_data = []

        print(f"Processing chunk {i} out of {len(url_chunks)}")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_url, url): url for url in chunk}
            for j, future in enumerate(concurrent.futures.as_completed(futures), start=1):
                url = futures[future]
                try:
                    data = future.result()
                    if data:
                        chunk_data.append(data)
                        internal_links = data.get('internal_links', set())
                        urls_to_visit.update(internal_links - visited)
                        print(f"Processed URL {j} in chunk {i}: {url}")
                except Exception as e:
                    logging.error(f"Error processing URL {url}: {e}", exc_info=True)


        all_data.extend(chunk_data)

        print(f"Total number of chunks saved: {i}")

    return all_data


@profile
# internal_link_crawler.py
def crawl_internal_links(domain): 
    visited = set()
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

@profile
# content_parser.py
def extract_data_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.title.string if soup.title else "No title found"
    author = soup.find('meta', attrs={'name': 'author'})
    author = author['content'] if author else "No author found"
    date = soup.find('time')
    date = date['datetime'] if date else "No date found"

    # Extract all text from the HTML content
    body = ' '.join(tag.get_text() for tag in soup.find_all(True))

    return {
        'title': title,
        'author': author,
        'date': date,
        'body': body
    }

# Helper function to load approved domains from a text file
def load_approved_domains():
    with open('domains.txt', 'r') as file:
        domains = [line.strip() for line in file if line.strip()]
    return domains

@profile
def main():
    domains = load_approved_domains()
    all_results = {}

    for domain in domains:
        logging.info(f'Crawling domain: {domain}')
        domain_data = crawl_domain(domain)
        all_results[domain] = {'Content': domain_data}

        # Extract harm reduction info and update data
        harm_reduction_info = extract_harm_reduction_info(' '.join(page['body'] for page in domain_data), domain)
        all_results[domain].update(harm_reduction_info)

    # Write data to CSV
    write_data_to_csv('results.csv', all_results)

if __name__ == '__main__':
    main()