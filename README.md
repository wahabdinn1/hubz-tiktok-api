# Social Media API

A unified API for **TikTok** and **Instagram** data scraping. Fetch user profiles, videos, reels, and analytics from a single endpoint.

## 🚀 Features

- **Multi-Platform**: TikTok + Instagram in one API
- **Organized Docs**: Clean Swagger UI with separate sections per platform
- **Session Persistence**: Instagram sessions can be exported/imported to avoid re-login
- **Docker Ready**: Deploy to Railway, Render, or any Docker host

## 🛠️ Quick Start

### Docker (Recommended)

```bash
docker build -t social-api .
docker run -p 8000:8000 \
  -e MS_TOKEN=your_tiktok_token \
  -e INSTAGRAM_SESSION=your_session_string \
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

| Variable             | Platform  | Description                          |
| -------------------- | --------- | ------------------------------------ |
| `MS_TOKEN`           | TikTok    | TikTok ms_token cookie               |
| `INSTAGRAM_SESSION`  | Instagram | Base64 session string (recommended!) |
| `INSTAGRAM_USERNAME` | Instagram | Username (only for first login)      |
| `INSTAGRAM_PASSWORD` | Instagram | Password (only for first login)      |

See `api/.env.example` for reference.

---

## 📸 Instagram Setup (One-Time Login)

To avoid repeated logins and reduce ban risk:

### Option 1: Browser Session Extraction (Recommended)

If API login is blocked:

```bash
python extract_instagram_session.py
```

1. Browser opens → Login manually (handle 2FA, etc.)
2. Press Enter in terminal
3. Copy session string → Add to `INSTAGRAM_SESSION` in Railway

### Option 2: API Login

If your IP isn't blocked:

1. Use `POST /api/instagram/login` with credentials
2. Call `GET /api/instagram/session/export`
3. Copy session → Add to `INSTAGRAM_SESSION` in Railway

### Option 3: Import via Swagger UI

Already have a session string?

1. Go to `/docs`
2. Use `POST /api/instagram/session/import`
3. Paste your session string

The API will auto-restore your session on every deploy!

---

## 📡 API Endpoints

### System

| Endpoint                             | Description               |
| ------------------------------------ | ------------------------- |
| `GET /api/token/status`              | TikTok token status       |
| `POST /api/token/update`             | Update TikTok token       |
| `GET /api/instagram/status`          | Instagram login status    |
| `POST /api/instagram/login`          | Login with credentials    |
| `POST /api/instagram/logout`         | Logout and clear session  |
| `GET /api/instagram/session/export`  | Export session for backup |
| `POST /api/instagram/session/import` | Import saved session      |

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

---

## 🌐 Deployment (Railway)

1. Push to GitHub
2. Connect repo to Railway
3. Add environment variables:
   - `MS_TOKEN` (TikTok)
   - `INSTAGRAM_SESSION` (Instagram - get from session export)
4. Deploy!

## 📄 License

MIT
