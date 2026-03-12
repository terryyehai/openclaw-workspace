#!/usr/bin/env python3
"""Download image from Gemini using Playwright"""

import asyncio
import sys
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch browser with download path
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
        
        # Create context with download directory
        context = await browser.new_context(
            downloads_path="/home/terry/Downloads"
        )
        
        page = await context.new_page()
        
        # Navigate to Gemini
        await page.goto("https://gemini.google.com/app/bf295c58e50e417f")
        await page.wait_for_timeout(3000)
        
        # Find and click the generated image to open lightbox
        # Then download from the lightbox
        
        # Wait for image to be visible
        try:
            await page.wait_for_selector('img[src*="gemini"]', timeout=10000)
        except:
            print("No image found")
            await browser.close()
            return
        
        # Get the image URL
        img_element = await page.query_selector('img[src*="gemini"]')
        if img_element:
            src = await img_element.get_attribute('src')
            print(f"Image URL: {src}")
            
            # Download the image
            if src:
                async with page.expect_download() as download_info:
                    await page.goto(src)
                download = await download_info.value
                path = await download.path()
                print(f"Downloaded to: {path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
