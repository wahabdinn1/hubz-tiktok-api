# TikTok API Python Backend

This is a Python Flask backend that uses [David Teather's TikTok-Api](https://github.com/davidteather/TikTok-Api) with Playwright for reliable TikTok data fetching.

## Setup

### 1. Install Python dependencies

```bash
cd python-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Playwright browsers

```bash
python -m playwright install
```

### 3. Get your ms_token

1. Go to [TikTok.com](https://www.tiktok.com) in your browser
2. Open DevTools (F12) → Application → Cookies
3. Find the `msToken` cookie and copy its value

### 4. Set environment variable

Create a `.env` file:

```bash
MS_TOKEN=your_ms_token_here
```

Or pass it as a header `X-MS-Token` with each request.

### 5. Run the server

```bash
python app.py
```

The server will run on `http://localhost:5000`

## API Endpoints

| Endpoint              | Method | Parameters          | Description             |
| --------------------- | ------ | ------------------- | ----------------------- |
| `/health`             | GET    | -                   | Health check            |
| `/api/user/posts`     | GET    | `username`, `count` | Get user's posts        |
| `/api/user/info`      | GET    | `username`          | Get user profile        |
| `/api/user/liked`     | GET    | `username`, `count` | Get user's liked videos |
| `/api/trending`       | GET    | `count`             | Get trending videos     |
| `/api/search/users`   | GET    | `query`, `count`    | Search users            |
| `/api/search/videos`  | GET    | `query`, `count`    | Search videos           |
| `/api/video/info`     | GET    | `url` or `id`       | Get video info          |
| `/api/hashtag/videos` | GET    | `name`, `count`     | Get hashtag videos      |
| `/api/sound/videos`   | GET    | `id`, `count`       | Get sound/music videos  |

## Example Usage

```bash
# Get user posts
curl "http://localhost:5000/api/user/posts?username=tiktok&count=10"

# Search videos
curl "http://localhost:5000/api/search/videos?query=funny&count=10"
```

## Running with Next.js

1. Start the Python backend: `python app.py`
2. Start Next.js: `npm run dev`
3. The Next.js API routes will call the Python backend

## Deployment Options

### Railway.app (Recommended - Free tier)

1. Create a new project on Railway
2. Connect your GitHub repo
3. Set `MS_TOKEN` environment variable
4. It will auto-deploy the Python backend

### Local with ngrok

1. Run the Python backend locally
2. Use ngrok to expose it: `ngrok http 5000`
3. Use the ngrok URL in your Next.js app
