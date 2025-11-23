'''
The script contains the logic of parsing data using Selenium and save it to a database.
'''


from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep

from load_django import *
from parser_app.models import Phone



def handle_browser():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options, service=ChromeService(ChromeDriverManager().install()))
    print('Driver successfully created.')
    return driver


def quit_driver(driver):
    print('Driver has been closed.')
    driver.quit()


def handle_url(driver, url: str):
    driver.get(url)
    print(f'Open link: {url}')
    sleep(2)


def go_to_the_page(driver):

    try:
        search_bar = driver.find_element(By.XPATH, '//div[@class="header-bottom"]//input[@type="search"]')
        print('Search bar has successfully found.')
        sleep(3)

        search_bar.click()

        phone_name = 'Apple iPhone 15 128GB Black'
        search_bar.send_keys(phone_name)

        print('Value has been successfully proceeded.')
        sleep(3)

    except NoSuchElementException:
        print('No search bar located on the page.')

    try:
        button = driver.find_element(By.XPATH, '//div[@class="header-bottom"]//input[@class="qsr-submit"]')
        print('Button is found.')
        button.click()
        sleep(3)

    except NoSuchElementException:
        print('No search button found.')


def handle_search_results(driver):
    try:
        first_result = wait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, '(//div[contains(@class,"description-wrapper")]//a)[1]')
            )
        )

        print('First result of matched query found.')
        first_result.click()
        print('Successful redirect...')
        sleep(5)

    except NoSuchElementException:
        print('Element has not been found.')


def extract_data_from_page(driver):
    print('*' * 100)

    try:
        specs_container = driver.find_element(By.XPATH, '//div[@class="br-pr-chr"]')
    except NoSuchElementException:
        specs_container = None
        print('Information about phone not found.')

    if specs_container:
        phone_data = {}

        try:
            phone_data['name'] = specs_container.find_element(By.XPATH, './/span[contains(text(), "Модель")]').find_element(By.XPATH, 'following-sibling::span').get_attribute('textContent').strip()
        except NoSuchElementException:
            phone_data['name'] = None

        try:
            phone_data['color'] = specs_container.find_element(By.XPATH,'.//span[contains(text(), "Колір")]').find_element(By.XPATH, 'following-sibling::span//a').get_attribute('textContent').strip()
        except NoSuchElementException:
            phone_data['color'] = None

        try:
            phone_data['memory'] = specs_container.find_element(By.XPATH, './/span[contains(text(), "Вбудована пам\'ять")]').find_element(By.XPATH, 'following-sibling::span//a').get_attribute('textContent').strip()
        except NoSuchElementException:
            phone_data['memory'] = None

        try:

            price_span = driver.find_element(By.XPATH, './/div[@class="br-pr-price main-price-block"]//span')
            price_strong = price_span.find_element(By.XPATH, 'following-sibling::strong').get_attribute('textContent')
            price_span_val = price_span.get_attribute('textContent')

            price = f'{price_span_val} {price_strong}'

            phone_data['price'] = ' '.join(price.split())
        except NoSuchElementException:
            phone_data['price'] = None

        try:
            phone_data['seller'] = specs_container.find_element(By.XPATH, './/span[contains(text(), "Виробник")]').find_element(By.XPATH,'following-sibling::span').get_attribute('textContent').strip()
        except NoSuchElementException:
            phone_data['seller'] = None

        try:
            img_urls = []
            img_array = driver.find_elements(By.XPATH, './/img[@class="dots-image"]')

            for img in img_array:
                src = img.get_attribute('src')

                if src:
                    img_urls.append(src)

            phone_data['photos'] = img_urls if img_urls else None
        except NoSuchElementException:
            phone_data['photos'] = None

        try:
            phone_data['code'] = driver.find_element(By.XPATH, '//div[@id="product_code"]//span[@class="br-pr-code-val"]').get_attribute('textContent').strip()
        except NoSuchElementException:
            phone_data['code'] = None

        try:
            reviews = specs_container.find_element(By.XPATH, './/div[@id="reviews-list"]').find_element(By.XPATH, '//div[@class="br-pt-bc-list"]').find_element(By.XPATH, "following-sibling::p").text.strip()
            phone_data['reviews'] = len(reviews)
        except NoSuchElementException:
            phone_data['reviews'] = None

        try:
            phone_data['diagonal'] = specs_container.find_element(By.XPATH, './/span[contains(text(), "Діагональ екрану")]').find_element(By.XPATH, 'following-sibling::span//a').get_attribute('textContent').strip()
        except NoSuchElementException:
            phone_data['diagonal'] = None

        try:
            phone_data['resolution'] = specs_container.find_element(By.XPATH, './/span[contains(text(), "Роздільна здатність екрану")]').find_element(By.XPATH, 'following-sibling::span//a').get_attribute('textContent').strip()
        except NoSuchElementException:
            phone_data['resolution'] = None

        try:
            phone_specs = {}
            container = specs_container.find_elements(By.XPATH, './/div')

            for data in container:
                name_specs = data.find_element(By.XPATH, './/span[1]').get_attribute('textContent').strip()
                value_specs = data.find_element(By.XPATH, './/span[2]').get_attribute('textContent').strip().replace('\xa0', ' ')

                name = ' '.join(name_specs.split())
                value = ' '.join(value_specs.split())

                if name_specs and value_specs:
                    phone_specs[name] = value

            phone_data['specs'] = phone_specs if phone_specs else None

        except NoSuchElementException:
            phone_data['specs'] = None

        for key, value in phone_data.items():
            print(f'{key}:{value}')


        object, created = Phone.objects.get_or_create(
            name = phone_data['name'],
            color = phone_data['color'],
            memory_capacity = phone_data['memory'],
            price = phone_data['price'],
            screen_diagonal = phone_data['diagonal'],
            display_resolution = phone_data['resolution'],
            seller = phone_data['seller'],
            product_code = phone_data['code'],
            reviews_amount = phone_data['reviews'],
            photos = phone_data['photos'],
            characteristics = phone_data['specs']
     )


if __name__ == '__main__':
    driver = handle_browser()
    sleep(1)
    handle_url(driver, 'https://brain.com.ua/')
    go_to_the_page(driver)
    handle_search_results(driver)
    extract_data_from_page(driver)
    sleep(10)
    quit_driver(driver)