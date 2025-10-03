# YouTube Audio Processing Pipeline

A FastAPI application that processes YouTube videos into audio clips with optional transcription and cloud storage.

## Features

- Download YouTube videos and extract audio
- Split audio using Voice Activity Detection (VAD)
- Optional Google Speech-to-Text transcription (Sinhala language)
- Optional Google Cloud Storage upload
- Optional database storage of clip metadata
- Clean REST API with FastAPI

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg:**
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up Google Cloud (optional):**
   - Create a Google Cloud project
   - Enable Speech-to-Text and Cloud Storage APIs
   - Create service account and download JSON key
   - Either set SERVICE_ACCOUNT_B64 or use `gcloud auth application-default login`

5. **Test database connection:**
   ```bash
   python create_tables.py
   ```

## Usage

1. **Start the application:**
   ```bash
   python run.py
   ```

2. **API Documentation:**
   Visit http://localhost:8000/docs for interactive API documentation

3. **Process a YouTube video:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/process-youtube" \
        -H "Content-Type: application/json" \
        -d '{
          "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
          "get_google_transcription": true,
          "upload_to_cloud_bucket": true,
          "add_to_transcription_service": true
        }'
   ```

## API Endpoints

### POST `/api/v1/process-youtube`

Process a YouTube video with the following options:

**Request Body:**
```json
{
  "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "get_google_transcription": false,
  "upload_to_cloud_bucket": false,
  "add_to_transcription_service": false,
  "vad_aggressiveness": 2,
  "start_padding": 1.0,
  "end_padding": 0.5
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed N clips",
  "video_metadata": { ... },
  "clips": [
    {
      "clip_name": "VIDEO_ID-001.wav",
      "duration": 5.2,
      "start_time": 10.5,
      "end_time": 15.7,
      "transcription": "transcribed text or null",
      "cloud_url": "https://storage.googleapis.com/... or null",
      "database_id": 123
    }
  ],
  "total_clips": 10
}
```

### GET `/health`

Health check endpoint.

## Configuration

Environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name
- `SERVICE_ACCOUNT_B64`: Base64 encoded service account JSON (optional)
- `DEBUG`: Enable debug mode (default: False)

## File Structure

```
audio_scraping/
├── app.py                    # Main FastAPI application
├── config.py                 # Configuration settings
├── database.py               # Database connection setup
├── create_tables.py          # Database initialization
├── run.py                    # Application startup script
├── requirements.txt          # Python dependencies
├── models/
│   └── audio.py             # Database models
├── schemas/
│   └── audio_schemas.py     # Pydantic request/response models
└── services/
    ├── youtube_processor.py  # YouTube video processing
    ├── transcription_service.py # Google Speech-to-Text
    └── cloud_storage.py      # Google Cloud Storage
```