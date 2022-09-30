import re
import json
import pandas
import requests
from bs4 import BeautifulSoup

def main(url, filename):

    get_request = requests.get(url)
    
    scraping = BeautifulSoup(get_request.text, 'html.parser')
    products = [product for product in scraping.find(class_='product-list product-list product-list--default')]

    # Get the data
    urls = []
    names = []
    skus = []
    initial_prices = []
    final_prices = []
    for product in products:
        url = product.find('a').get('href')
        domain = '' if url.startswith('https://www.plaisio.gr') else 'https://www.plaisio.gr'
        urls.append(domain+url)
        names.append(product.find(class_='product-title').text)
        skus.append(product.find(class_='sku').text)
        try:
            initial_price = "%.2f" % float(product.find(class_='price').find(class_='from-price').text)
        except ValueError:
            initial_price = ""
        initial_prices.append(initial_price)
        final_prices.append("%.2f" % float(product.find(class_='price').find(class_='price').text))

    redirect_requests = [requests.get(url) for url in urls]
    redirect_scrapings = [BeautifulSoup(redirect_request.text, 'html.parser') for redirect_request in redirect_requests]

    scripts = [json.loads(redirect_scraping.find('script', type='application/ld+json').text) for redirect_scraping in redirect_scrapings]
    brands = [brand['brand']['name'] for brand in scripts]
    availabilities = [availability['offers']['availability'].partition('schema.org/')[2] for availability in scripts]
    
    ean_scripts = [redirect_scraping.find(class_='pdp-imagelist').script.text for redirect_scraping in redirect_scrapings]
    product_eans_re = [re.search('"productEan":"([0-9]*)"', script) for script in ean_scripts]
    product_eans = [x.group(1) if x else 'None' for x in product_eans_re]

    df = pandas.DataFrame(
        {
            'url': urls,
            'ProductName': names,
            'Sku': skus,
            'Brand': brands,
            'Final Price': final_prices,
            'Availability': availabilities,
            'Initial Price': initial_prices,
            'Ean': product_eans
        }
    )
    df.to_csv(filename)

if __name__=='__main__':
    urls = [
        'https://www.plaisio.gr/pc-perifereiaka/laptops/windows-laptops',
        'https://www.plaisio.gr/anavathmisi-diktia/anavathmisi-pc/koutia-desktop/',
        'https://www.plaisio.gr/smart-tech-gadgets/wearables/smartwatch',
    ]
    filenames = [
        'products.csv',
        'desktop_cases.csv',
        'smartwatches.csv',
    ]
    for url, filename in zip(urls, filenames):
        main(url, filename)
        print(f'{filename} is ready')
