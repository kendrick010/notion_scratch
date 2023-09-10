import os
from dotenv import load_dotenv
import requests
import csv
import dateutil.parser
from pytz import timezone

def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """

    load_dotenv()

    api_key = os.environ.get('NOTION_API_KEY')
    database_id = os.environ.get('NOTION_DATABASE_ID')

    base_url = 'https://api.notion.com/v1'
    header = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json', 'Notion-Version': '2022-06-28'}
    
    url = f'{base_url}/databases/{database_id}/query'

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=header)

    data = response.json()

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        response = requests.post(url, json=payload, headers=header)
        data = response.json()
        results.extend(data["results"])

    return results

if __name__ == '__main__':

    pages = get_pages()

    with open('notion.csv', 'w', newline='') as file:
        writer = csv.writer(file)

        for page in pages:
            created = page['created_time']
            props = page["properties"]
            role = props["Position"]["multi_select"][0]["name"]

            created = dateutil.parser.parse(created)
            created = created.astimezone(timezone('US/Pacific'))
            created = created.strftime('%m/%d/%Y %H:%M:%S')

            writer.writerow([role, created])