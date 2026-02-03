"""
Instagram Scraper using Playwright
Scrapes public Instagram profiles without requiring login.
"""

import asyncio
import json
from typing import Dict, Any, List
from playwright.async_api import async_playwright

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"


async def scrape_instagram_profile(username: str) -> Dict[str, Any]:
    """Scrape Instagram profile using Playwright (public profiles only)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()
        
        try:
            url = f"https://www.instagram.com/{username}/"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            # Check if profile exists
            not_found = await page.query_selector('text="Sorry, this page isn\'t available."')
            if not_found:
                return {"error": "Profile not found"}
            
            # Extract data from meta tags
            profile_data = await page.evaluate('''() => {
                const data = {
                    username: null,
                    full_name: null,
                    biography: null,
                    follower_count: null,
                    following_count: null,
                    media_count: null,
                    profile_pic_url: null,
                    is_private: false,
                    is_verified: false
                };
                
                // Helper to parse count strings like "1.2K", "1M"
                const parseCount = (str) => {
                    if (!str) return null;
                    str = str.replace(/,/g, '');
                    if (str.toLowerCase().includes('k')) return Math.round(parseFloat(str) * 1000);
                    if (str.toLowerCase().includes('m')) return Math.round(parseFloat(str) * 1000000);
                    return parseInt(str);
                };
                
                // Extract from og:title - "Name (@username) • Instagram photos and videos"
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle) {
                    const match = ogTitle.content.match(/^(.+?)\\s*\\(@(.+?)\\)/);
                    if (match) {
                        data.full_name = match[1].trim();
                        data.username = match[2];
                    }
                }
                
                // Profile pic from og:image
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage) data.profile_pic_url = ogImage.content;
                
                // Stats from og:description - "123 Followers, 456 Following, 78 Posts"
                const ogDesc = document.querySelector('meta[property="og:description"]');
                if (ogDesc) {
                    const desc = ogDesc.content;
                    const followerMatch = desc.match(/(\\d+[.,]?\\d*[KMkm]?)\\s*Followers/i);
                    const followingMatch = desc.match(/(\\d+[.,]?\\d*[KMkm]?)\\s*Following/i);
                    const postsMatch = desc.match(/(\\d+[.,]?\\d*[KMkm]?)\\s*Posts/i);
                    
                    if (followerMatch) data.follower_count = parseCount(followerMatch[1]);
                    if (followingMatch) data.following_count = parseCount(followingMatch[1]);
                    if (postsMatch) data.media_count = parseCount(postsMatch[1]);
                }
                
                // Verified badge
                data.is_verified = !!document.querySelector('[aria-label="Verified"]');
                
                // Private account
                const bodyText = document.body.innerText;
                data.is_private = bodyText.includes("This account is private") || 
                                  bodyText.includes("This Account is Private");
                
                return data;
            }''')
            
            return profile_data
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            await browser.close()


async def scrape_instagram_posts(username: str, count: int = 10) -> List[Dict[str, Any]]:
    """Scrape Instagram posts using Playwright (public profiles only)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()
        
        try:
            url = f"https://www.instagram.com/{username}/"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            # Scroll to load more posts
            for _ in range(min(count // 12 + 1, 5)):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
            
            # Extract post links and thumbnails
            posts = await page.evaluate(f'''() => {{
                const posts = [];
                const links = document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]');
                
                for (let i = 0; i < Math.min(links.length, {count}); i++) {{
                    const link = links[i];
                    const href = link.getAttribute('href');
                    const shortcode = href.match(/\\/(?:p|reel)\\/([\\w-]+)/)?.[1];
                    
                    if (shortcode && !posts.find(p => p.code === shortcode)) {{
                        const img = link.querySelector('img');
                        posts.push({{
                            code: shortcode,
                            thumbnail_url: img ? img.src : null,
                            is_reel: href.includes('/reel/'),
                            url: 'https://www.instagram.com' + href
                        }});
                    }}
                }}
                return posts;
            }}''')
            
            return posts[:count]
            
        except Exception as e:
            print(f"Error scraping posts: {e}")
            return []
        finally:
            await browser.close()


async def scrape_instagram_post(shortcode: str) -> Dict[str, Any]:
    """Scrape a single Instagram post/reel by shortcode."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()
        
        try:
            # Try /p/ first, then /reel/
            url = f"https://www.instagram.com/p/{shortcode}/"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            post_data = await page.evaluate('''() => {
                const data = {
                    shortcode: null,
                    caption: null,
                    like_count: null,
                    comment_count: null,
                    owner_username: null,
                    thumbnail_url: null,
                    video_url: null,
                    is_video: false
                };
                
                const parseCount = (str) => {
                    if (!str) return null;
                    str = str.replace(/,/g, '');
                    if (str.toLowerCase().includes('k')) return Math.round(parseFloat(str) * 1000);
                    if (str.toLowerCase().includes('m')) return Math.round(parseFloat(str) * 1000000);
                    return parseInt(str);
                };
                
                // Thumbnail from og:image
                const ogImage = document.querySelector('meta[property="og:image"]');
                if (ogImage) data.thumbnail_url = ogImage.content;
                
                // Video URL from og:video
                const ogVideo = document.querySelector('meta[property="og:video"]');
                if (ogVideo) {
                    data.video_url = ogVideo.content;
                    data.is_video = true;
                }
                
                // Parse description for likes, comments, caption
                const ogDesc = document.querySelector('meta[property="og:description"]');
                if (ogDesc) {
                    const desc = ogDesc.content;
                    
                    const likeMatch = desc.match(/(\\d+[.,]?\\d*[KMkm]?)\\s*likes?/i);
                    if (likeMatch) data.like_count = parseCount(likeMatch[1]);
                    
                    const commentMatch = desc.match(/(\\d+[.,]?\\d*[KMkm]?)\\s*comments?/i);
                    if (commentMatch) data.comment_count = parseCount(commentMatch[1]);
                }
                
                // Owner from og:title - "@username on Instagram"
                const ogTitle = document.querySelector('meta[property="og:title"]');
                if (ogTitle) {
                    const match = ogTitle.content.match(/@(\\w+)/);
                    if (match) data.owner_username = match[1];
                }
                
                return data;
            }''')
            
            post_data['shortcode'] = shortcode
            post_data['url'] = url
            return post_data
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            await browser.close()


async def scrape_instagram_reels(username: str, count: int = 10) -> List[Dict[str, Any]]:
    """Scrape Instagram reels with full details using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        page = await context.new_page()
        
        try:
            # Go directly to user's reels tab
            url = f"https://www.instagram.com/{username}/reels/"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            
            # Scroll to load more reels
            for _ in range(min(count // 12 + 1, 5)):
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await asyncio.sleep(1)
            
            # Extract reel shortcodes
            reel_codes = await page.evaluate(f'''() => {{
                const codes = [];
                const links = document.querySelectorAll('a[href*="/reel/"]');
                
                for (let i = 0; i < Math.min(links.length, {count}); i++) {{
                    const href = links[i].getAttribute('href');
                    const match = href.match(/\\/reel\\/([\\w-]+)/);
                    if (match && !codes.includes(match[1])) {{
                        codes.push(match[1]);
                    }}
                }}
                return codes;
            }}''')
            
            await browser.close()
            
            # Now fetch details for each reel
            reels = []
            for code in reel_codes[:count]:
                reel_data = await scrape_instagram_post(code)
                if "error" not in reel_data:
                    reel_data['is_reel'] = True
                    reels.append(reel_data)
            
            return reels
            
        except Exception as e:
            print(f"Error scraping reels: {e}")
            return []
        finally:
            if browser.is_connected():
                await browser.close()


async def scrape_instagram_posts_detailed(username: str, count: int = 10) -> List[Dict[str, Any]]:
    """Scrape Instagram posts with full details using Playwright."""
    try:
        # First get the list of posts (shortcodes)
        base_posts = await scrape_instagram_posts(username, count)
        
        detailed_posts = []
        for post in base_posts:
            # Fetch full details for each post
            details = await scrape_instagram_post(post['code'])
            
            if "error" not in details:
                # Merge details with base info (base info has url, is_reel which might be useful)
                merged = {**post, **details}
                detailed_posts.append(merged)
            else:
                # Fallback to base info if detailed fetch fails
                detailed_posts.append(post)
                
        return detailed_posts
        
    except Exception as e:
        print(f"Error scraping detailed posts: {e}")
        return []
