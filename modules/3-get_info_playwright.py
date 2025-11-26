'''
Script for parsing data using Playwright
'''

from playwright.async_api import async_playwright, Error
from load_django import *
from parser_app.models import Phone
from asgiref.sync import sync_to_async
import asyncio


@sync_to_async
def get_new_items():
    return list(Phone.objects.filter(status='New').order_by('id'))

@sync_to_async
def mark_item_done(phone: Phone):
    phone.status = 'Done'
    phone.save()


async def main():
    phone = await get_new_items()
    try:
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    channel='chrome',
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"]
                )
            except Error as nameError:
                print(f'Error while launch browser: {nameError}')
                return

            try:
                context = await browser.new_context(
                    permissions=["geolocation"],
                    geolocation={"latitude": 50.45, "longitude": 30.52},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                    viewport={"width": 1400, "height": 700},
                    locale="en-US",
                    timezone_id="Europe/Kyiv"
                )
            except Error as nameError:
                print(f'Failed to create browser context - {nameError}')
                await browser.close()
                return

            for data in phone:
                link = 'https://brain.com.ua/'
                page = await context.new_page()

                await page.goto(link)
                await page.wait_for_timeout(3000)

                try:
                    await page.locator('xpath=//div[@class="header-bottom"]//input[@type="search"]').click()
                    await page.wait_for_timeout(3000)
                except Error as nameError:
                    print(f'An error occurred: {nameError}')

                text = 'Apple iPhone 15 128GB Black'
                try:
                    await page.locator('xpath=//div[@class="header-bottom"]//input[@type="search"]').fill(text)
                    await page.wait_for_timeout(3000)
                except Error as nameError:
                    print(f'An error occurred: {nameError}')

                try:
                    await page.locator('xpath=//div[@class="header-bottom"]//input[@class="qsr-submit"]').click()
                    await page.wait_for_timeout(3000)
                except Error as nameError:
                    print(f'An error occurred: {nameError}')

                try:
                    await page.locator('xpath=(//div[contains(@class,"description-wrapper")]//a)[1]').click()
                    await page.wait_for_timeout(3000)
                except Error as nameError:
                    print(f'An error occurred: {nameError}')

                print('*' * 100)

                container = await page.query_selector_all('xpath=//div[@class="br-pr-chr"]')

                for con in container:
                    phone_data = {}

                    try:
                        name_prod = await page.query_selector('xpath=.//h2[@class="prod-title"]//span[contains(text(), "Характеристики")]//following-sibling::span')
                        phone_data['name'] = (await name_prod.text_content()).strip() if name_prod else None
                    except:
                        phone_data['name'] = None

                    try:
                        color_prod = await con.query_selector('xpath=.//span[contains(text(), "Колір")]//following-sibling::span//a')
                        phone_data['color'] = (await color_prod.text_content()).strip() if color_prod else None
                    except:
                        phone_data['color'] = None

                    try:
                        memory = await con.query_selector('xpath=.//span[contains(text(), "Вбудована пам\'ять")]//following-sibling::span//a')
                        phone_data['memory'] = (await memory.text_content()).strip() if memory else None
                    except:
                        phone_data['memory'] = None

                    try:
                        price_raw = await page.query_selector('xpath=.//div[@class="br-pr-price main-price-block"]//span')
                        price_val_raw = await price_raw.query_selector('xpath=following-sibling::strong')
                        price = (await price_raw.text_content()).strip() if price_raw else None
                        price_val = (await price_val_raw.text_content()).strip() if price_val_raw else None

                        price_group = f'{price} {price_val}'

                        phone_data['price'] = price_group
                    except:
                        phone_data['price'] = None

                    try:
                        seller = await con.query_selector('xpath=.//span[contains(text(), "Виробник")]//following-sibling::span')
                        phone_data['seller'] = (await seller.text_content()).strip() if seller else None
                    except:
                        phone_data['seller'] = None

                    try:
                        img_url = []
                        imgs = await page.query_selector_all('xpath=.//img[@class="dots-image"]')

                        for img in imgs:
                            src = await img.get_attribute('src')

                            if src:
                                img_url.append(src)

                        phone_data['photos'] = img_url if img_url else None
                    except:
                        phone_data['photos'] = None

                    try:
                        code = await page.query_selector('xpath=//div[@id="product_code"]//span[@class="br-pr-code-val"]')
                        phone_data['code'] = (await code.text_content()).strip() if code else None
                    except:
                        phone_data['code'] = None

                    try:
                        reviews = await con.query_selector_all('xpath=//div[@id="reviews-list"]//div[@class="br-pt-bc-list"]')
                        count_reviews = len(reviews)
                        phone_data['reviews'] = count_reviews
                    except:
                        phone_data['reviews'] = 0

                    try:
                        diagonal = await con.query_selector('xpath=.//span[contains(text(), "Діагональ екрану")]//following-sibling::span//a')
                        phone_data['diagonal'] = (await diagonal.text_content()).strip() if diagonal else None
                    except:
                        phone_data['diagonal'] = None

                    try:
                        resolution = await con.query_selector('xpath=.//span[contains(text(), "Роздільна здатність екрану")]//following-sibling::span//a')
                        phone_data['resolution'] = (await resolution.text_content()).strip() if resolution else None
                    except:
                        phone_data['resolution'] = None

                    try:
                        specs = {}
                        specs_container = await con.query_selector_all('xpath=.//div')

                        for item in specs_container:
                            name_specs_raw = await item.query_selector('xpath=.//span[1]')
                            value_specs_raw = await item.query_selector('xpath=.//span[2]')

                            name_specs_edited = (await name_specs_raw.text_content()).strip()
                            value_specs_edited = (await value_specs_raw.text_content()).strip().replace('\xa0', ' ')


                            name = ' '.join(name_specs_edited.split()).strip()
                            value = ' '.join(value_specs_edited.split()).strip()

                            if name_specs_edited and value_specs_edited:
                                specs[name] = value

                        phone_data['specs'] = specs if specs else None

                    except:
                        phone_data['specs'] = None

                    for key, value in phone_data.items():
                        print(f'{key}:{value}')

                await save_to_db(phone_data)

                await mark_item_done(phone)

            await browser.close()


    except Exception as nameError:
        print(f'Error: {nameError}')


@sync_to_async
def save_to_db(phone_data):
    object, created = Phone.objects.get_or_create(
        name=phone_data['name'],
        color=phone_data['color'],
        memory_capacity=phone_data['memory'],
        price=phone_data['price'],
        screen_diagonal=phone_data['diagonal'],
        display_resolution=phone_data['resolution'],
        seller=phone_data['seller'],
        product_code=phone_data['code'],
        reviews_amount=phone_data['reviews'],
        photos=phone_data['photos'],
        characteristics=phone_data['specs']
    )


if __name__ == '__main__':
    asyncio.run(main())

