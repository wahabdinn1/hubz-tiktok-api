# TikTok Standalone API (FastAPI)

A robust, standalone API for fetching trending TikTok videos and creators. Built with **FastAPI** and **Playwright**, this API provides a simple, documented interface for scraping TikTok Creative Center data.

## Features

- **FastAPI**: High performance, easy to use, and automatic interactive documentation.
- **Playwright Scraping**: Reliably visualizes and extracts data from dynamic TikTok pages.
- **Auto-Docs**: Swagger UI (`/docs`) and ReDoc (`/redoc`) available out of the box.
- **CORS Enabled**: Configured to allow requests from any origin (`*`), making it easy to integrate with your frontend apps.

## Prerequisites

- Python 3.8+
- Chrome/Chromium (installed automatically via Playwright)

## Installation

1.  Navigate to the api directory:

    ```bash
    cd api
    ```

2.  Run the setup script (installs dependencies and browsers):
    ```bash
    ./setup.sh
    ```
    _Alternatively, manually install:_
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

## Running the API

Start the server using `uvicorn`:

```bash
# From api directory
source venv/bin/activate  # Activate virtual env
uvicorn app:app --reload --host 0.0.0.0 --port 5000
```

The API will be available at **http://localhost:5000**.

## API Documentation

Once the server is running, visit **[http://localhost:5000/docs](http://localhost:5000/docs)** to see the interactive Swagger UI. You can test endpoints directly from the browser!

### Endpoints

#### Trending

- `GET /api/trending/videos`
- `GET /api/trending/creators`

#### Users

- `GET /api/user/{username}` - Profile info
- `GET /api/user/{username}/videos` - User's video feed
- `GET /api/user/{username}/liked` - User's liked videos

#### Videos

- `GET /api/video/{video_id}` - Details & Download URL
- `GET /api/video/{video_id}/comments` - Video comments

#### Search

- `GET /api/search` - Search TikTok (params: `q`, `type`)

#### Hashtags & Music

- `GET /api/hashtag/{name}` - Hashtag info
- `GET /api/hashtag/{name}/videos` - Videos with this hashtag
- `GET /api/music/{music_id}` - Music info
- `GET /api/music/{music_id}/videos` - Videos using this sound

**Example Response:**

```json
{
  "status": "success",
  "result": [
    {
      "id": "...",
      "desc": "...",
      "author": { ... }
    }
  ]
}
```
