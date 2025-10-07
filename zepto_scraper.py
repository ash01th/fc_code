import asyncio
from playwright.async_api import Playwright, async_playwright
import json

async def run(playwright: Playwright, url: str):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page(viewport={"width": 1600, "height": 900})
    await page.goto(url, wait_until="networkidle")

    # 1. DEFINE THE SELECTOR FOR THE MAIN PRODUCT CARD/CONTAINER
    # This div seems to wrap all the info for a single product.
    product_card_selector = "div.c5SZXs" 

    try:
        # Wait for the first product card to appear on the page
        await page.wait_for_selector(product_card_selector, timeout=15000)
        print("Product cards are visible. Starting scrape...")
    except Exception as e:
        print(f"Could not find product cards on the page. The website structure might have changed. Error: {e}")
        await browser.close()
        return

    # 2. GET ALL THE PRODUCT CARD ELEMENTS
    product_cards = await page.query_selector_all(product_card_selector)
    print(f"Found {len(product_cards)} product cards on the page.")

    scraped_data = []

    # 3. LOOP THROUGH EACH CARD AND EXTRACT THE DETAILS
    for card in product_cards:
        # Find the name element WITHIN the current card
        name_element = await card.query_selector('[data-slot-id="ProductName"]')
        
        # Find the price element WITHIN the current card
        price_element = await card.query_selector('[data-slot-id="Price"]')

        # Ensure both elements were found before trying to get text
        if name_element and price_element:
            name = await name_element.inner_text()
            price = await price_element.inner_text()
            
            scraped_data.append({
                "product_name": name.strip(),
                "price": price.strip()
            })

    await browser.close()
    
    # 4. PRINT THE FINAL RESULTS
    print("\n--- Scraped Data ---")
    for item in scraped_data:
        print(f"Product: {item['product_name']}, Price: {item['price']}")
    
    return scraped_data


async def main():
    async with async_playwright() as playwright:
        result = await run(playwright, url="https://www.zeptonow.com/search?query=bread")
        with open("zepto_data.json","w") as output_file:
            json.dump(result,output_file,indent=4)

        print(result)

if __name__ == "__main__":
    asyncio.run(main())