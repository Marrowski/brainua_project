'''
The script contains the logic for parsing data from a web resource and saving it to a database.
'''


from load_django import *
from parser_app.models import Phone
import requests
from bs4 import BeautifulSoup
from django.db import IntegrityError
from pprint import pprint

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "uk-UA,uk;q=0.9,ru-RU,ru;q=0.8,en-US,en;q=0.7",
    "Referer": "https://brain.com.ua/",
    "Connection": "keep-alive",
}


url = 'https://brain.com.ua/ukr/Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html'


response = requests.get(url, headers=headers)
if response.status_code == 200:
    print('Connection established successfully.')
    soup = BeautifulSoup(response.text, 'html.parser')
    phone = {}

    container = soup.find('div', attrs={'class':'br-pr-chr'})

    try:
        phone['color'] = (container.find('span', string='Колір').find_next('a').text.strip())
    except AttributeError:
        phone['color'] = None

    try:
        phone['memory'] = container.find('span', string="Вбудована пам'ять").find_next('a').text.strip()
    except AttributeError:
        phone['memory'] = None

    try:
        phone['seller'] = (container.find('span', string='Виробник').find_next('span').text.strip())
    except AttributeError:
        phone['seller'] = None

    price_wrapper = soup.find('div', class_='price-wrapper')

    try:
        price_span = price_wrapper.find('span').text.strip()
        price_strong = price_wrapper.find('strong').text.strip()

        phone['default_price'] = f'{price_span} {price_strong}'
    except AttributeError:
        phone['default_price'] = None

    try:
        image = soup.find_all('img', class_='dots-image')
        phone['photos'] = [img.get('src') for img in image]

    except AttributeError:
        phone['photos'] = None

    try:
        phone['diagonal'] = (container.find('h3', string='Дисплей').find_parent('div', class_='br-pr-chr-item').
                             find('span', string='Діагональ екрану').find_next('a').text.strip())
    except AttributeError:
        phone['diagonal'] = None

    try:
        phone['series'] = (container.find('span', string='Модель').find_next('span').text.strip())
    except AttributeError:
        phone['series'] = None

    try:
        phone['resolution'] = (container.find('span', string='Роздільна здатність екрану').find_next('span').text.strip())
    except AttributeError:
        phone['resolution'] = None

    try:
        phone['reviews'] = len(soup.find_all('div', class_='br-pt-bc-item'))

    except AttributeError:
        phone['reviews'] = None

    try:
        phone['code'] = soup.find('div', class_='product-code-num').find('span', class_='br-pr-code-val').text.strip()

    except AttributeError:
        phone['code'] = None


    try:
        specs_dict = {}

        rows = container.select('.br-pr-chr-item > div > div')

        for data in rows:
            name = data.find('span')
            value = name.find_next_sibling()

            k = name.text.strip()
            v = ' '.join(value.text.split())

            specs_dict[k] = v

        phone['specs'] = specs_dict if specs_dict else None


    except AttributeError:
        phone['specs'] = None


    print('*' * 100)
    pprint(phone)


    object, created = Phone.objects.get_or_create(
        name=phone.get('series'),
        color=phone.get('color'),
        memory_capacity=phone.get('memory'),
        price=phone.get('default_price'),
        screen_diagonal=phone.get('diagonal'),
        display_resolution=phone.get('resolution'),
        seller=phone.get('seller'),
        product_code=phone.get('code'),
        reviews_amount=phone.get('reviews'),
        photos=phone.get('photos'),
        characteristics=phone.get('specs'),
    )

else:
    print(f'Connection error:{response.status_code}.')



















