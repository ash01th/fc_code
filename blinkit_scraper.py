import asyncio
from playwright.async_api import Playwright, async_playwright
import json

async def run(playwright: Playwright, url: str):
    #create a browser instance and load the page
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page(viewport={"width": 1600, "height": 900})
    
    await page.goto(url)

    #blinkit requires location to be set before viewing products
    try:
        #wait for the location input field to appear
        #location input field selector
        location_input_selector = 'input[name="select-locality"]'
        await page.wait_for_selector(location_input_selector, timeout=10000)
        print("Location input field found. Entering location...")

        #click the input field and type the location as peelamedu
        await page.click(location_input_selector)
        await page.fill(location_input_selector, "peelamedu")

        #wait for the dropdown suggestion and click the first element
        location_dropdown_selector = 'div[class*="LocationSearchList__LocationListContainer"]'
        try:
            await page.wait_for_selector(location_dropdown_selector, timeout=5000)
            print("Location dropdown found. Clicking first option...")
            # Use query_selector to get the first matching div
            first_location_element = await page.query_selector(location_dropdown_selector)
            if first_location_element:
                await first_location_element.click()
            else:
                raise Exception("First location dropdown element not found")
        except Exception as e:
            print(f"Error finding or clicking first location dropdown element: {e}")
            await browser.close()
            return []

        #wait 5 seconds after clicking the location for loading
        print("Waiting 5 seconds after selecting location...")
        await page.wait_for_timeout(5000)
    except Exception as e:
        print(f"Error during location selection: {e}")
        await browser.close()
        return []

    #selector for product card
    product_card_selector = "div[class*='tw-flex tw-h-full tw-flex-col']"

    try:
        # Wait for the first product card to appear
        await page.wait_for_selector(product_card_selector, timeout=15000)
        print("Product cards are visible. Starting scrape...")
    except Exception as e:
        print(f"Could not find product cards on the page. Error: {e}")
        await browser.close()
        return []

    #get all product card elements
    product_cards = await page.query_selector_all(product_card_selector)
    print(f"Found {len(product_cards)} product cards on the page.")

    scraped_data = []

    #iterate through each card and extract name and price
    for index, card in enumerate(product_cards):
        #selector for product name element
        name_element = await card.query_selector('div[class*="tw-text-300 tw-font-semibold tw-line-clamp-2"]')
        #selector for price element
        price_element = await card.query_selector('div[class*="tw-text-200 tw-font-semibold"]')

        #debugging details about the card
        if not name_element:
            print(f"Card {index + 1}: Product name element not found")
        if not price_element:
            print(f"Card {index + 1}: Price element not found")

       
        if name_element or price_element:
            product_name = await name_element.inner_text() if name_element else "N/A"
            price = await price_element.inner_text() if price_element else "N/A"

            scraped_data.append({
                "product_name": product_name.strip() if product_name else "",
                "price": price.strip() if price else ""
            })
        else:
            print(f"Card {index + 1}: Skipped due to missing both name and price elements")

    await browser.close()

    #printing scraped data
    print("\n--- Scraped Data ---")
    for item in scraped_data:
        print(f"Product: {item['product_name']}, Price: {item['price']}")

    return scraped_data

async def main():
    async with async_playwright() as playwright:
        result = await run(playwright, url="https://blinkit.com/s/?q=bread")
        with open("blinkit_data.json", "w") as output_file:
            json.dump(result, output_file, indent=4)

        print(result)

if __name__ == "__main__":
    asyncio.run(main())