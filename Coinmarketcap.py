import requests
import csv
import os

def fetch_details(ids, api_key):
    url_info = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}
    params = {'id': ",".join(map(str, ids))}
    response = requests.get(url_info, headers=headers, params=params)
    return response.json()

api_key = os.getenv('COINMARKETCAP')
cryptos_fetched = 0
start = 1
crypto_details = []

while cryptos_fetched < 9000:
    url_listing = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {'start': start, 'limit': 100, 'convert': 'USD'}
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': api_key}
    response = requests.get(url_listing, headers=headers, params=parameters)
    data = response.json()

    if 'data' not in data:
        print("Fin ou erreur de l'API, arrêt de la récupération.")
        break

    crypto_ids = [crypto['id'] for crypto in data['data']]
    details = fetch_details(crypto_ids, api_key)

    for id, info in details['data'].items():
        twitter_urls = info.get('urls', {}).get('twitter', [])
        twitter = twitter_urls[0] if twitter_urls else None

        website_urls = info.get('urls', {}).get('website', [])
        website = website_urls[0] if website_urls else None

        crypto_details.append({
            'name': info.get('name'),
            'twitter': twitter,
            'website': website,
            'categories': info.get('tags', []),
            'chain': info.get('platform', {}).get('name') if info.get('platform') else 'N/A'
        })

    cryptos_fetched += len(data['data'])
    start += len(data['data'])

csv_file = "coinmarketcap-data.csv"
csv_columns = ['name', 'twitter', 'website', 'categories', 'chain']

try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in crypto_details:
            writer.writerow(data)
except IOError:
    print("I/O error lors de l'écriture du fichier CSV")
