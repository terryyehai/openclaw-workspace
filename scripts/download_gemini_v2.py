#!/usr/bin/env python3
"""
Download image from Gemini using Playwright with existing browser profile
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch with existing user data to maintain login session
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="/home/terry/.openclaw/browser/openclaw/user-data",
            headless=False,  # Need GUI to see the download
            downloads_path="/home/terry/Downloads",
            args=['--no-sandbox']
        )
        
        # Get the page
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Navigate to the conversation
        await page.goto("https://gemini.google.com/app/bf295c58e50e417f")
        await page.wait_for_timeout(3000)
        
        # Click on the image to open lightbox
        try:
            # Find and click the generated image
            img_selector = "img[src*='lh3']"
            await page.wait_for_selector(img_selector, timeout=10000)
            await page.click(img_selector)
            await page.wait_for_timeout(2000)
            
            # Click download button
            download_btn = "button:has-text('下載原尺寸')"
            async with page.expect_download() as download_info:
                await page.click(download_btn)
            
            download = await download_info.value
            print(f"Downloaded to: {download.path}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        # Keep browser open for a moment
        await asyncio.sleep(2)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
