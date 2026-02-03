#!/usr/bin/env python3
"""
Instagram Session Extractor (Browser Method)
Opens a browser where you login manually, then extracts your session.
"""

import json
import base64
import asyncio
from playwright.async_api import async_playwright

async def main():
    print("=" * 50)
    print("Instagram Session Extractor (Browser Method)")
    print("=" * 50)
    print("\nThis will open a browser window.")
    print("Login to Instagram manually, then press Enter here.\n")
    
    async with async_playwright() as p:
        # Launch visible browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Go to Instagram
        await page.goto("https://www.instagram.com/accounts/login/")
        
        print("🌐 Browser opened! Please login to Instagram.")
        print("   (Handle 2FA, challenges, etc. in the browser)")
        print("\n" + "=" * 50)
        input("Press ENTER here after you've logged in successfully...")
        print("=" * 50)
        
        # Extract cookies
        cookies = await context.cookies()
        
        # Find important cookies
        session_cookies = {}
        for cookie in cookies:
            if cookie['domain'] in ['.instagram.com', 'instagram.com']:
                session_cookies[cookie['name']] = cookie['value']
        
        await browser.close()
        
        # Check if we got sessionid
        if 'sessionid' not in session_cookies:
            print("❌ No session found. Make sure you're logged in!")
            return
        
        # Create session data for instagrapi
        session_data = {
            "cookies": session_cookies,
            "ig_did": session_cookies.get("ig_did", ""),
            "ig_nrcb": session_cookies.get("ig_nrcb", ""),
            "mid": session_cookies.get("mid", ""),
            "sessionid": session_cookies.get("sessionid", ""),
            "csrftoken": session_cookies.get("csrftoken", ""),
            "ds_user_id": session_cookies.get("ds_user_id", ""),
            "rur": session_cookies.get("rur", ""),
        }
        
        # Encode for storage
        session_str = base64.b64encode(json.dumps(session_data).encode()).decode()
        
        print("\n✅ Session extracted successfully!")
        print("\n" + "=" * 50)
        print("🔐 YOUR SESSION STRING:")
        print("=" * 50)
        print(session_str)
        print("=" * 50)
        
        # Save to file
        with open("instagram_session.txt", "w") as f:
            f.write(session_str)
        print("\n📁 Saved to: instagram_session.txt")
        print("📋 Add to Railway as: INSTAGRAM_SESSION")

if __name__ == "__main__":
    asyncio.run(main())
