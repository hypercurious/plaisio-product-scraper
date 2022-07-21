import re
import pandas
import requests
from bs4 import BeautifulSoup

def main(link, filename):

    get_request = requests.get(link)
    
    scraping = BeautifulSoup(get_request.text, 'html.parser')
    products = [product for product in scraping.find_all(class_='column item')]

    # Get the data
    urls = []
    names = []
    skus = []
    initial_prices = []
    final_prices = []
    availabilities = [] # all availabilities are 'Εξαντλήθηκε', because the website loads the value 'Εξαντλήθηκε' for all products and after a while it loads the correct value
    for product in products:
        urls.append('https://plaisio.gr'+product.find('a').get('href'))
        names.append(product.find(class_='product-title').text)
        skus.append(product.find(class_='sku').text)
        initial_prices.append(product.find(class_='price').find(class_='from-price').text)
        final_prices.append(product.find(class_='price').find(class_='price').text)
        availabilities.append(product.find(class_='stock-indication-text').text)

    brands = [name.split(' ')[0] for name in names]

    redirect_requests = [requests.get(url) for url in urls]
    redirect_scrapings = [BeautifulSoup(redirect_request.text, 'html.parser') for redirect_request in redirect_requests]

    scripts = [redirect_scraping.find(class_='pdp-imagelist').script.text for redirect_scraping in redirect_scrapings]
    product_eans_re = [re.search('"productEan":"([0-9]*)"', script) for script in scripts]
    product_eans = [x.group(1) if x else 'None' for x in product_eans_re]

    df = pandas.DataFrame()
    df['url'] = urls
    df['ProductName'] = names
    df['Sku'] = skus
    df['Brand'] = brands
    df['Final Price'] = final_prices
    df['Availability'] = availabilities
    df['Initial Price'] = initial_prices
    df['Ean'] = product_eans
    df.to_csv(filename)

if __name__=='__main__':
    links = [
        'https://www.plaisio.gr/pc-perifereiaka/laptops/windows-laptops',
        'https://www.plaisio.gr/anavathmisi-diktia/anavathmisi-pc/koutia-desktop/',
        'https://www.plaisio.gr/smart-tech-gadgets/wearables/smartwatch'
    ]
    filenames = [
        'products.csv',
        'desktop_cases.csv',
        'smartwatches.csv'
    ]
    for link, filename in zip(links, filenames):
        main(link, filename)
        print('Done')
