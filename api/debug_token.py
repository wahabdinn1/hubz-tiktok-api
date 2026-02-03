
import asyncio
import sys
from playwright.async_api import async_playwright

async def debug_token():
    log_file = open("api/debug.log", "w")
    def log(msg):
        print(msg)
        log_file.write(msg + "\n")
        log_file.flush()
        
    log("Launching browser...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            log("Browser launched")
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            log("Navigating to TikTok...")
            await page.goto("https://www.tiktok.com/", wait_until="domcontentloaded", timeout=60000)
            log("Navigation complete")
            
            # Screenshot
            await page.screenshot(path="token_debug.png")
            log("Screenshot saved to token_debug.png")
            
            # Cookies
            cookies = await context.cookies()
            found_ms = False
            log(f"Total cookies: {len(cookies)}")
            for c in cookies:
                log(f" - {c['name']}")
                if c['name'] == 'msToken':
                    log(f"   => VALUE FOUND: {c['value'][:10]}...")
                    found_ms = True
            
            if not found_ms:
                log("FAILURE: msToken not found.")
            else:
                log("SUCCESS: msToken found.")
                
            await browser.close()
            
        except Exception as e:
            log(f"Error: {e}")
            import traceback
            traceback.print_exc(file=log_file)

if __name__ == "__main__":
    asyncio.run(debug_token())
