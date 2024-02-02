import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def export_data_to_csv(data, filename):
    try:
        df = pd.DataFrame(data)
        if 'keywords' in df.columns:
            df['keywords'] = df['keywords'].apply(lambda x: ', '.join([f'{k}: {v}' for k, v in x.items()]))
        df.to_csv(filename, index=False)
        logging.info('Data successfully exported to scraped_data.csv')
    except Exception as e:
        logging.error(f"Error exporting data to CSV: {e}", exc_info=True)

all_scraped_data = [
{'title': 'Test Title 1', 'date': '2023-01-01', 'author': 'Author 1', 'body': 'Test body content 1', 'keywords': {'dose': '50mg', 'substances': 'Substance A'}, 'url': 'https://exampledomain1.com', 'domain': 'exampledomain1.com'},
{'title': 'Test Title 2', 'date': '2023-02-01', 'author': 'Author 2', 'body': 'Test body content 2', 'keywords': {'peak': '2 - 4 hours', 'onset': '30 - 60 minutes'}, 'url': 'https://exampledomain2.com', 'domain': 'exampledomain2.com'}
]

# Call the export function
export_data_to_csv(all_scraped_data, 'scraped_data.csv')

# Assuming all_scraped_data is provided
# export_data_to_csv(all_scraped_data)