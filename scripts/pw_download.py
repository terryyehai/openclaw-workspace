#!/usr/bin/env python3
"""
Playwright download skill for Gemini images
"""
import asyncio
from playwright.async_api import async_playwright

async def download_gemini_image():
    download_path = "/home/terry/Downloads"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
        
        context = await browser.new_context(
            downloads_path=download_path
        )
        
        page = await context.new_page()
        
        # Go to Gemini conversation
        await page.goto("https://gemini.google.com/app/bf295c58e50e417f")
        await page.wait_for_timeout(5000)
        
        # Find and click the image
        try:
            img = await page.query_selector("img[src*='lh3']")
            if img:
                await img.click()
                await page.wait_for_timeout(2000)
                
                # Click download
                download_btn = await page.query_selector("button:has-text('下載原尺寸')")
                if download_btn:
                    async with page.expect_download() as download_info:
                        await download_btn.click()
                    
                    download = await download_info.value
                    path = await download.path()
                    print(f"SUCCESS:{path}")
                else:
                    print("ERROR: Download button not found")
            else:
                print("ERROR: Image not found")
        except Exception as e:
            print(f"ERROR:{e}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(download_gemini_image())
