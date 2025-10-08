import asyncio
from playwright.async_api import Playwright, async_playwright
import json

async def run(playwright: Playwright, url: str):
    #create browser instance and load the page
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page(viewport={"width": 1600, "height": 900})
    #wait until page content is done loading
    await page.goto(url, wait_until="networkidle")
    #define the selector for product card 
    product_card_selector = "div.c5SZXs" 

    try:
        # Wait for the  product card to appear on the page
        await page.wait_for_selector(product_card_selector, timeout=15000)
        print("Product cards are visible. Starting scrape...")
    except Exception as e:
        print(f"Could not find product cards on the page. The website structure might have changed. Error: {e}")
        await browser.close()
        return

    # get all the product card elements
    product_cards = await page.query_selector_all(product_card_selector)
    print(f"Found {len(product_cards)} product cards on the page.")

    scraped_data = []

    #iterate through each card and extract name and price
    for card in product_cards:
        # Find the name element inside the current card
        name_element = await card.query_selector('[data-slot-id="ProductName"]')
        
        # Find the price element inside the current card
        price_element = await card.query_selector('[data-slot-id="Price"]')

        
        if name_element and price_element:
            name = await name_element.inner_text()
            price = await price_element.inner_text()
        #store data as list of key value pairs   
            scraped_data.append({
                "product_name": name.strip(),
                "price": price.strip()
            })
    #close browser
    await browser.close()
    #printing scraped data
    print("\n--- Scraped Data ---")
    for item in scraped_data:
        print(f"Product: {item['product_name']}, Price: {item['price']}")
    
    return scraped_data

#run the main function
async def main():
    async with async_playwright() as playwright:
        result = await run(playwright, url="https://www.zeptonow.com/search?query=bread")
        with open("data/zepto_data.json","w") as output_file:
            json.dump(result,output_file,indent=4)

        print(result)

asyncio.run(main())