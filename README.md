# Social Media API

A unified API for **TikTok** and **Instagram** data scraping. Fetch user profiles, videos, reels, and analytics from a single endpoint.

## 🚀 Features

- **Multi-Platform**: TikTok + Instagram in one API
- **Organized Docs**: Clean Swagger UI with separate sections per platform
- **Session Persistence**: Instagram sessions saved to avoid re-login
- **Docker Ready**: Deploy to Railway, Render, or any Docker host

## 🛠️ Quick Start

### Docker (Recommended)

```bash
docker build -t social-api .
docker run -p 8000:8000 \
  -e MS_TOKEN=your_tiktok_token \
  -e INSTAGRAM_USERNAME=your_ig_username \
  -e INSTAGRAM_PASSWORD=your_ig_password \
  social-api
```

### Manual Setup

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
uvicorn app:app --reload --port 8000
```

## 🔑 Environment Variables

| Variable             | Platform  | Description             |
| -------------------- | --------- | ----------------------- |
| `MS_TOKEN`           | TikTok    | TikTok ms_token cookie  |
| `INSTAGRAM_USERNAME` | Instagram | Your Instagram username |
| `INSTAGRAM_PASSWORD` | Instagram | Your Instagram password |

See `api/.env.example` for reference.

## 📡 API Endpoints

### System

| Endpoint                    | Description                   |
| --------------------------- | ----------------------------- |
| `GET /`                     | API info and available routes |
| `GET /api/token/status`     | TikTok token status           |
| `POST /api/token/update`    | Update TikTok token           |
| `GET /api/instagram/status` | Instagram login status        |

---

### 🎵 TikTok

| Endpoint                                 | Description         |
| ---------------------------------------- | ------------------- |
| `GET /api/tiktok/user/{username}`        | User profile        |
| `GET /api/tiktok/user/{username}/videos` | User's videos       |
| `GET /api/tiktok/user/{username}/liked`  | User's liked videos |
| `GET /api/tiktok/video/{id}`             | Video details       |
| `GET /api/tiktok/video/{id}/comments`    | Video comments      |
| `GET /api/tiktok/trending/videos`        | Trending videos     |
| `GET /api/tiktok/trending/creators`      | Trending creators   |
| `GET /api/tiktok/search`                 | Search TikTok       |
| `GET /api/tiktok/hashtag/{name}`         | Hashtag info        |
| `GET /api/tiktok/music/{id}`             | Music/sound info    |

---

### 📸 Instagram

| Endpoint                                        | Description    |
| ----------------------------------------------- | -------------- |
| `GET /api/instagram/user/{username}`            | User profile   |
| `GET /api/instagram/user/{username}/posts`      | User's posts   |
| `GET /api/instagram/user/{username}/reels`      | User's reels   |
| `GET /api/instagram/media/{shortcode}`          | Media details  |
| `GET /api/instagram/media/{shortcode}/comments` | Media comments |
| `GET /api/instagram/hashtag/{name}`             | Hashtag info   |
| `GET /api/instagram/hashtag/{name}/posts`       | Hashtag posts  |

> **Note**: The `shortcode` is the part after `/p/` or `/reel/` in Instagram URLs.  
> Example: `instagram.com/p/ABC123xyz/` → shortcode is `ABC123xyz`

## 🌐 Deployment (Railway)

1. Push to GitHub
2. Connect repo to Railway
3. Add environment variables in Railway dashboard
4. Deploy!

## 📄 License

MIT
