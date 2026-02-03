# TikTok Standalone API

A high-performance, containerized API for fetching TikTok videos, user profiles, and trending content. Built with **FastAPI** and **Playwright** to bypass bot detection.

## 🚀 Features

- **Comprehensive Data**: Fetch user profiles, videos (no watermark), comments, manufacturing, and search results.
- **Bot Bypass**: Uses Playwright and dynamic `ms_token` generation to handle TikTok's security parameters.
- **Dockerized**: Ready for deployment on Railway, Render, or any Docker-compatible platform.
- **Zero-Downtime Updates**: Update your `ms_token` at runtime without restarting the server.
- **Auto-Docs**: Interactive Swagger UI (`/docs`) and ReDoc (`/redoc`).

## 🛠️ Installation & Local Run

1.  **Clone & Enter Directory**:

    ```bash
    git clone <your-repo-url>
    cd tiktok-api
    ```

2.  **Using Docker (Recommended)**:

    ```bash
    docker build -t tiktok-api .
    docker run -p 8000:8000 -e PORT=8000 tiktok-api
    ```

3.  **Manual Python Setup**:
    ```bash
    cd api
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    playwright install chromium
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
    ```

## 🌐 Deployment (Railway)

This project is optimized for [Railway](https://railway.app/).

1.  **Push to GitHub**.
2.  **Deploy on Railway**: Connect your repo. Railway will automatically detect the `Dockerfile`.
3.  **Environment Variables**:
    - `MS_TOKEN`: (Optional) Initial token string.
4.  **Domain**: Generate a domain in Railway Settings > Networking.

Your API will be live at `https://<your-project>.up.railway.app`.

## 🔑 Token Management

TikTok requires an `ms_token` (cookie) to authenticate requests. This API uses a smart fallback system:

### How it works:

1.  **Server Token First**: The API tries using the server's `MS_TOKEN` (from env variable).
2.  **Fallback to User Token**: If the server token returns an empty response, it automatically retries with your provided `ms_token`.

### Providing Your Token:

Every endpoint has an optional `ms_token` query parameter visible in **Swagger UI (`/docs`)**:

```
GET /api/user/tiktok?ms_token=YOUR_TOKEN_HERE
```

### Admin Endpoints:

- `POST /api/token/update?token=...`: Update the server's global token at runtime.
- `POST /api/token/auto`: Auto-generate a token (with synthetic fallback).
- `GET /api/token/status`: Check if a token is configured.

## 📡 API Endpoints

Explore the full interactive documentation at `/docs`.

### Users

- `GET /api/user/{username}`: Profile details.
- `GET /api/user/{username}/videos`: Video feed (includes pinned status).
- `GET /api/user/{username}/liked`: Liked videos.

### Videos

- `GET /api/video/{id}`: Metadata & download URL.
- `GET /api/video/{id}/comments`: Fetch comments.

### Search & Trending

- `GET /api/search?q=...`: Search users/videos.
- `GET /api/trending/videos`: Trending content.

### Hashtags & Music

- `GET /api/hashtag/{name}`
- `GET /api/music/{id}`
