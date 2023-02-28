import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import csv
from random import choice


# def get_html(url):
#     r = requests.get(url)
#     if r.ok:
#         return r.text
#     print(r.status_code)


def get_proxy():
    html = requests.get('https://free-proxy-list.net/').text
    soup = BeautifulSoup(html, 'lxml')

    trs = soup.find('table', class_='table table-striped table-bordered').find_all('tr')[1:17]

    proxies = []

    for tr in trs:
        tds = tr.find_all('td')
        ip = tds[0].text.strip()
        port = tds[1].text.strip()
        schema = 'https' if 'yes' in tds[6].text.strip() else 'http'
        proxy = {'schema': schema, 'address': f'{schema}://{ip}:{port}'}
        proxies.append(proxy)

    return choice(proxies)

def get_json(url):
    p = get_proxy()
    proxy = {p['schema']: p['address']}

    r = requests.get(url, proxies=proxy, timeout=5)
    if r.ok:
        return r.json()
    print(r.status_code)

    
def write_csv(data, csv_name):
    with open(csv_name, 'a') as f:
        order = ['id', 'product_name', 'product_brand_id', 'product_brand_name', 'product_full_price', 'product_sale_price', 'reviews_count']
        writer = csv.DictWriter(f, fieldnames=order)
        writer.writerow(data)

        
def get_data(all_data):
    ids = all_data['data']['products']
    for i in range(len(ids)):
        product_id = ids[i]['id']
        product_name = ids[i]['name']
        product_brand_id = ids[i]['brandId']
        product_brand_name = ids[i]['brand']
        product_full_price = ids[i]['priceU'] // 100
        product_sale_price = ids[i]['salePriceU'] // 100
        reviews_count = ids[i]['feedbacks']
        data = {
            'id': product_id,
            'product_name': product_name,
            'product_brand_id': product_brand_id,
            'product_brand_name': product_brand_name,
            'product_full_price': product_full_price,
            'product_sale_price': product_sale_price,
            'reviews_count': reviews_count
            }
        write_csv(data, 'test.csv')


def make_all(url):
    data = get_json(url)
    get_data(data)


def main():
    url = 'https://catalog.wb.ru/catalog/men_clothes1/catalog?appType=1&cat=8144&couponsGeo=2,12,7,3,6,18,21&curr=rub&dest=123585693&emp=0&lang=ru&locale=ru\
        &page={}&pricemarginCoeff=1.0&reg=0&regions=80,64,38,4,83,33,68,70,69,30,86,40,1,22,66,31,48,110&sort=popular&spp=0'
    urls = [url.format(i) for i in range(1, 101)]

    with Pool(10) as p:
        p.map(make_all, urls)


if __name__=='__main__':
    main()