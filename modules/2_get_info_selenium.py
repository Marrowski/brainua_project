from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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
        search_bar = driver.find_element(By.XPATH, "//input[@type='search']")
        print('Search bar has successfully found.')
        sleep(1)

        phone_name = 'Apple iPhone 15 128GB Black'
        search_bar.send_keys(phone_name)
        print('Value has been successfully proceeded')
        sleep(1)

    except NoSuchElementException:
        print('No search bar located on the page.')

    try:
        button = driver.find_element(By.XPATH, '//input[@class="search-button-first-form"]')
        print('Button is found')
        button.click()
        sleep(1)

    except NoSuchElementException:
        print('No search button found.')


def handle_search_results(driver):
    try:
        first_result = driver.find_element(By.XPATH, '//div[@class="col-lg-3 col-md-4 col-sm-6 col-xs-6 product-wrapper br-pcg-product-wrapper"][1]')
        print('First result of matched query found.')
        first_result.click()
        print('Successful redirect...')
        sleep(1)

    except NoSuchElementException:
        print('Element has not been found.')


def extract_data_from_page(driver):
    print('*' * 100)

    try:
        content = driver.find_element(By.XPATH, '//div[@class="br-body br-body-product"]')

    except NoSuchElementException:
        content = None
        print('Page content not found')

    if content:
        phone_data = {}

        try:
            phone_data['name'] = content.find_element(By.XPATH, '//h1[@class="main-title"]').text
        except NoSuchElementException:
            phone_data['name'] = None

        if not phone_data['name']:
            return

        try:
            phone_data['color'] = content.find_element('//span[contains(text(), "Колір")]').find_element(By.XPATH, 'following::a[1]').text.strip()

        except NoSuchElementException:
            phone_data['color'] = None










if __name__ == '__main__':
    pass