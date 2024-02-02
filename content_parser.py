from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

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

if __name__ == "__main__":
    test_html_content = "<html><head><title>Test Title</title><meta name='author' content='Test Author'></head><body><time datetime='2023-04-01'>April 1, 2023</time><p>This is a test paragraph.</p></body></html>"
    try:
        extracted_data = extract_data_from_html(test_html_content)
        logging.info(f"Extracted Data: {extracted_data}")
    except Exception as e:
        logging.error(f'Error occurred while extracting data: {e}', exc_info=True)