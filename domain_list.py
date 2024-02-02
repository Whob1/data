import logging

logging.basicConfig(level=logging.INFO)

def load_approved_domains():
    """
    Loads the list of approved domains from a predefined text file 'domains.txt'.
    
    Returns:
        approved_domains (list): A list of domains read from the text file.
    """
    approved_domains = []
    try:
        # Open the domains.txt file and read domains into a list
        with open('domains.txt', 'r') as file:
            for domain in file:
                domain = domain.strip()
                if domain.startswith('http://') or domain.startswith('https://'):
                    approved_domains.append(domain)
                    logging.info(f"Domain added: {domain}")
                else:
                    logging.warning(f"Ignoring malformed URL: {domain}")
    except Exception as e:
        logging.error("An error occurred while loading domains:", exc_info=True)
    return approved_domains

if __name__ == '__main__':
    try:
        domains = load_approved_domains()
        logging.info('Approved domains:')
        for domain in domains:
            logging.info(domain)
    except Exception as e:
        logging.error("Error loading domains:", exc_info=True)