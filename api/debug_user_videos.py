
import asyncio
import os
import json
from TikTokApi import TikTokApi

# Mock env var for token if needed, or rely on auto-fetch logic from app if I imported it, 
# but for standalone debug I'll try without or use empty string and hope for public access or use existing env.
# The user's app.py uses get_current_token(). I'll just rely on MS_TOKEN env var if present.

async def inspect_user_videos():
    ms_token = os.environ.get("MS_TOKEN", "")
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        
        username = "tiktok"
        count = 5
        print(f"Fetching {count} videos for {username}...")
        
        user = api.user(username=username)
        videos = []
        i = 0
        async for video in user.videos(count=count):
            start = i
            data = video.as_dict
            # Dump the first video's data keys to see structure
            if i == 0:
                print("First Video Keys:", data.keys())
                # specific checks for pinned
                print("Pinned/Top related fields:")
                for k, v in data.items():
                    if "pin" in k.lower() or "top" in k.lower():
                        print(f"  {k}: {v}")
            
            videos.append(data)
            i += 1
            # We want to see if it stops at 5 naturally
            if i > count + 5: # Limit just in case it runs wild
                print("Exceeded count + 5, forcing break")
                break
        
        print(f"Total videos fetched: {len(videos)}")

if __name__ == "__main__":
    asyncio.run(inspect_user_videos())
