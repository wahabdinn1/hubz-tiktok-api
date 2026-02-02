import os
import asyncio
import json
from typing import Optional, List, Dict, Any, Union
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from TikTokApi import TikTokApi
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="TikTok Standalone API",
    description="A robust, standalone API for fetching TikTok trending videos and creators.",
    version="1.0.0"
)

# Configure CORS
# Allow all origins by default for maximum compatibility with other apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models for Response Documentation
class Author(BaseModel):
    uniqueId: str
    nickname: str = ""
    avatarThumb: str = ""

class Video(BaseModel):
    id: str
    desc: str
    cover: str
    playCount: int = 0
    diggCount: int = 0
    author: Author
    video: Optional[Dict[str, Any]] = None

class Creator(BaseModel):
    id: str
    uniqueId: str
    nickname: str
    avatarThumb: str
    followerCount: int = 0
    videoCount: int = 0
    verified: bool = False
    diggCount: int = 0

class TrendingResponse(BaseModel):
    status: str
    result: List[Union[Video, Creator]]
    totalPosts: Optional[int] = None
    totalCreators: Optional[int] = None
    message: Optional[str] = None

# --- Token Management ---

# Global state for runtime token updates (avoids redeploys)
RUNTIME_MS_TOKEN = os.getenv("MS_TOKEN", "")

def get_current_token() -> str:
    """Get the currently active ms_token."""
    global RUNTIME_MS_TOKEN
    return RUNTIME_MS_TOKEN

async def fetch_new_token() -> Optional[str]:
    """Attempts to fetch a fresh ms_token using Playwright."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            await page.goto("https://www.tiktok.com/", wait_until="domcontentloaded", timeout=30000)
            cookies = await context.cookies()
            for cookie in cookies:
                if cookie['name'] == 'msToken':
                    return cookie['value']
        except Exception as e:
            print(f"Failed to auto-fetch token: {e}")
        finally:
            await browser.close()
    return None

@app.post("/api/token/update", tags=["System"])
async def update_token(token: str = Query(..., description="The new ms_token string")):
    """Update the ms_token at runtime without restarting the server."""
    global RUNTIME_MS_TOKEN
    RUNTIME_MS_TOKEN = token
    return {
        "status": "success", 
        "message": "Token updated successfully. Subsequent requests will use the new token.", 
        "result": {"preview": token[:10] + "..." if len(token) > 10 else token}
    }

@app.post("/api/token/auto", tags=["System"])
async def auto_refresh_token():
    """Attempt to automatically scrape a fresh ms_token from TikTok."""
    global RUNTIME_MS_TOKEN
    new_token = await fetch_new_token()
    if new_token:
        RUNTIME_MS_TOKEN = new_token
        return {"status": "success", "message": "Token auto-refreshed", "token": new_token}
    raise HTTPException(status_code=500, detail="Failed to retrieve ms_token automatically.")

@app.get("/api/token/status", tags=["System"])
async def get_token_status():
    """Check if a token is configured."""
    token = get_current_token()
    return {
        "configured": bool(token), 
        "preview": token[:10] + "..." if token and len(token) > 10 else None
    }

# --- Helper Functions ---

async def get_trending_videos(count: int = 10, country: str = 'id') -> Dict[str, Any]:
    """Scrapes trending videos using Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            url = f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/pc/en?countryCode={country}"
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            # Wait for content to load
            await asyncio.sleep(5)
            
            # Scroll to load more content
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

            # Extract data from window.__NEXT_DATA__
            try:
                next_data = await page.evaluate('() => window.__NEXT_DATA__')
                raw_videos = []
                if next_data:
                    props = next_data.get('props', {}).get('pageProps', {}).get('data', {})
                    if 'videos' in props:
                        raw_videos = props['videos']
                
                results = []
                for i, video in enumerate(raw_videos):
                    if i >= count:
                        break
                        
                    video_id = video.get('itemId', video.get('id', str(i)))
                    desc = video.get('title', '')
                    cover = video.get('cover', '')
                    item_url = video.get('itemUrl', '')
                    
                    # Extract author info from URL
                    unique_id = ''
                    if '@' in item_url:
                        parts = item_url.split('@')
                        if len(parts) > 1:
                            unique_id = parts[1].split('/')[0]
                            
                    results.append({
                        'id': video_id,
                        'desc': desc,
                        'cover': cover,
                        'playCount': 0, # Not available in simple JSON
                        'diggCount': 0,
                        'author': {
                            'nickname': unique_id,
                            'uniqueId': unique_id,
                            'avatarThumb': ''
                        }
                    })
                    
                if results:
                    return {"status": "success", "result": results, "totalPosts": len(results)}

            except Exception as e:
                print(f"Error handling __NEXT_DATA__: {e}")
                
            return {"status": "error", "message": "Failed to extract trending videos"}

        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await browser.close()

async def get_trending_creators(count: int = 10, country: str = 'id') -> Dict[str, Any]:
    """Scrapes trending creators using Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            url = f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/creator/pc/{country}"
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Wait for content
            await asyncio.sleep(5)
            
            # Extract data from __NEXT_DATA__
            try:
                next_data = await page.evaluate('() => window.__NEXT_DATA__')
                raw_creators = []
                if next_data:
                    props = next_data.get('props', {}).get('pageProps', {}).get('data', {})
                    if 'creators' in props:
                        raw_creators = props['creators']
                
                results = []
                for i, creator in enumerate(raw_creators):
                    if i >= count:
                        break
                        
                    c_id = creator.get('creatorId', creator.get('id', str(i)))
                    nickname = creator.get('nickName', creator.get('nickname', ''))
                    unique_id = creator.get('uniqueId', creator.get('handle', ''))
                    avatar = creator.get('avatarUrl', creator.get('avatar', ''))
                    followers = creator.get('followerCount', 0)
                    
                    results.append({
                        'id': c_id,
                        'nickname': nickname,
                        'uniqueId': unique_id,
                        'avatarThumb': avatar,
                        'followerCount': followers
                    })
                    
                if results:
                    return {"status": "success", "result": results, "totalCreators": len(results)}

            except Exception as e:
                print(f"Error handling creator __NEXT_DATA__: {e}")
            
            return {"status": "error", "message": "Failed to extract trending creators"}

        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await browser.close()

# --- Helper Functions (Updated) ---

async def get_tiktok_api():
    """Returns a TikTokApi instance context manager"""
    ms_token = os.getenv("MS_TOKEN")
    return await TikTokApi().create_async(ms_token=ms_token)

# --- Routes ---

@app.get("/", tags=["General"])
async def root():
    """Welcome endpoint listing available API services."""
    return {
        "message": "Welcome to the TikTok Standalone API",
        "docs_url": "/docs",
        "endpoints": {
            "trending_videos": "/api/trending/videos",
            "trending_creators": "/api/trending/creators",
            "user_profile": "/api/user/{username}",
            "user_feed": "/api/user/{username}/videos",
            "video_details": "/api/video/{video_id}",
            "video_comments": "/api/video/{video_id}/comments",
            "search": "/api/search",
            "hashtag": "/api/hashtag/{name}",
            "music": "/api/music/{music_id}"
        }
    }

# --- Trending Endpoints ---

@app.get("/api/trending/videos", response_model=TrendingResponse, tags=["Trending"])
async def trending_videos(
    count: int = Query(10, ge=1, le=50, description="Number of items to return"),
    country: str = Query("id", description="Country code")
):
    """Fetch trending videos from Creative Center."""
    data = await get_trending_videos(count=count, country=country)
    if data.get("status") == "error":
        raise HTTPException(status_code=500, detail=data.get("message"))
    return data

@app.get("/api/trending/creators", response_model=TrendingResponse, tags=["Trending"])
async def trending_creators(
    count: int = Query(10, ge=1, le=50, description="Number of items to return"),
    country: str = Query("id", description="Country code")
):
    """Fetch trending creators from Creative Center."""
    data = await get_trending_creators(count=count, country=country)
    if data.get("status") == "error":
        raise HTTPException(status_code=500, detail=data.get("message"))
    return data

# --- User Endpoints ---

@app.get("/api/user/{username}", tags=["User"])
async def user_info(username: str):
    """Get user profile details."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            user = api.user(username=username)
            user_data = await user.info()
            return {"status": "success", "user": user_data}
        except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{username}/videos", tags=["User"])
async def user_videos(username: str, count: int = 10):
    """Get user's video feed."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            user = api.user(username=username)
            videos = []
            async for video in user.videos(count=count):
                videos.append(video.as_dict)
            return {"status": "success", "videos": videos}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user/{username}/liked", tags=["User"])
async def user_liked(username: str, count: int = 10):
    """Get user's liked videos (if public)."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            user = api.user(username=username)
            videos = []
            async for video in user.liked(count=count):
                videos.append(video.as_dict)
            return {"status": "success", "videos": videos}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# --- Video Endpoints ---

@app.get("/api/video/{video_id}", tags=["Video"])
async def video_details(video_id: str):
    """Get video details and download URL."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            video = api.video(id=video_id)
            info = await video.info()
            return {"status": "success", "video": info}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/video/{video_id}/comments", tags=["Video"])
async def video_comments(video_id: str, count: int = 20):
    """Get comments for a video."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            video = api.video(id=video_id)
            comments = []
            async for comment in video.comments(count=count):
                comments.append(comment.as_dict)
            return {"status": "success", "comments": comments}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# --- Search Endpoints ---

@app.get("/api/search", tags=["Search"])
async def search(q: str, type: str = "video", count: int = 10):
    """Search for users, videos, or hashtags."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            results = []
            search_obj_type = type
            if type == "video":
                search_obj_type = "item"
                
            async for item in api.search.search_type(q, obj_type=search_obj_type, count=count):
                results.append(item.as_dict)
            return {"status": "success", "results": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# --- Hashtag & Music Endpoints ---

@app.get("/api/hashtag/{name}", tags=["Hashtag"])
async def hashtag_info(name: str):
    """Get hashtag details."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            tag = api.hashtag(name=name)
            info = await tag.info()
            return {"status": "success", "hashtag": info}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hashtag/{name}/videos", tags=["Hashtag"])
async def hashtag_videos(name: str, count: int = 10):
    """Get videos for a hashtag."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            tag = api.hashtag(name=name)
            videos = []
            async for video in tag.videos(count=count):
                videos.append(video.as_dict)
            return {"status": "success", "videos": videos}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/music/{music_id}", tags=["Music"])
async def music_info(music_id: str):
    """Get music/sound details."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            sound = api.sound(id=music_id)
            info = await sound.info()
            return {"status": "success", "music": info}
        except Exception as e:
             raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/music/{music_id}/videos", tags=["Music"])
async def music_videos(music_id: str, count: int = 10):
    """Get videos using a specific sound."""
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[get_current_token()], num_sessions=1, sleep_after=3)
        try:
            sound = api.sound(id=music_id)
            videos = []
            async for video in sound.videos(count=count):
                videos.append(video.as_dict)
            return {"status": "success", "videos": videos}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
