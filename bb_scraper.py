import asyncio
from playwright.async_api import Playwright, async_playwright
import json

async def run(playwright: Playwright, url: str):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page(viewport={"width": 1600, "height": 900})
    await page.goto(url, wait_until="networkidle")

    #scroll down to load lazy-loaded images
    #important since we capture product names from image alt attribute
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(5000)  # Wait 2 seconds for images to load

    #selector for product card
    product_card_selector = "li.PaginateItems___StyledLi-sc-1yrbjdr-0"

    try:
    #wait for the first product card to appear on the page
        await page.wait_for_selector(product_card_selector, timeout=15000)
        print("Product cards are visible. Starting scrape...")
    except Exception as e:
        print(f"Could not find product cards on the page.Error: {e}")
        await browser.close()
        return

    #get all product card elements
    product_cards = await page.query_selector_all(product_card_selector)
    print(f"Found {len(product_cards)} product cards on the page.")

    scraped_data = []

    #iterate through the product cards and then images and then alt attribute for product name
    for index, card in enumerate(product_cards):
        image_element = await card.query_selector('img[class*="DeckImage"]')
        #price element selector
        price_element = await card.query_selector('span.Pricing___StyledLabel-sc-pldi2d-1')

        #debugging  details about the card
        if not image_element:
            print(f"Card {index + 1}: Image element not found")
            #inner html contents for debugging
            image_container = await card.query_selector('div.DeckImage___StyledDiv-sc-1mdvxwk-1')
            if image_container:
                image_html = await image_container.inner_html()
                print(f"Card {index + 1} Image Container HTML: {image_html[:200]}...")
        if not price_element:
            print(f"Card {index + 1}: Price element not found")

        
        if image_element or price_element:
            product_name = await image_element.get_attribute('alt') if image_element else "N/A"
            price = await price_element.inner_text() if price_element else "N/A"
            
            scraped_data.append({
                "product_name": product_name.strip() if product_name else "",
                "price": price.strip() if price else ""
            })
        else:
            print(f"Card {index + 1}: Skipped due to missing both image and price elements")

    await browser.close()
    #printing scraped data
    print("\n--- Scraped Data ---")
    for item in scraped_data:
        print(f"Product: {item['product_name']}, Price: {item['price']}")
    
    return scraped_data

async def main():
    async with async_playwright() as playwright:
        result = await run(playwright, url="https://www.bigbasket.com/ps/?q=bread")
        with open("bb_data.json", "w") as output_file:
            json.dump(result, output_file, indent=4)

        print(result)


asyncio.run(main())