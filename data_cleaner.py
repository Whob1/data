import re
import logging

logging.basicConfig(level=logging.INFO)

keywords = ['dose', 'substances', 'peak', 'onset', 'duration', 'adverse effects', 'interactions']
keyword_patterns = {
    'dose': r'dose[:\s]*([\w\s]+mg)',
    'substances': r'substances[:\s]*([\w\s,]+)',
    'peak': r'peak[:\s]*(\d+\s*-\s*\d+\s*hours?)',
    'onset': r'onset[:\s]*(\d+\s*-\s*\d+\s*minutes?)',
    'duration': r'duration[:\s]*(\d+\s*-\s*\d+\s*hours?)',
    'adverse effects': r'adverse effects[:\s]*([\w\s,]+)',
    'interactions': r'interactions[:\s]*([\w\s,]+)'
}

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
        else:
            extracted_data[keyword] = None
        
    return extracted_data

def process_extracted_data(raw_data):
    logging.info("Cleaning and extracting data from raw text")
    cleaned_text = clean_text(raw_data)
    keyword_data = extract_keywords(cleaned_text)
    return keyword_data

if __name__ == "__main__":
    sample_text = """
    This is a test text mentioning dose: 50mg, substances: Substance A, B, C, peak: 2 - 4 hours, onset: 20 - 60 minutes, 
    duration: 5 - 8 hours, adverse effects: nausea, headache, interactions: Substance D, E.
    """
    try:
        extracted_data = process_extracted_data(sample_text)
        for key, value in extracted_data.items():
            logging.info(f"{key}: {value}")
    except Exception as e:
        logging.error(f"Error occurred in data cleaning module: {e}", exc_info=True)