# Audio Processing UI

A modern, dark-themed web interface for processing YouTube videos into audio clips with transcription and cloud storage capabilities.

## Features

- **YouTube Video Processing**: Enter a YouTube URL to download and split videos into audio clips
- **Voice Activity Detection**: Automatically segments audio using advanced VAD algorithms
- **Random Preview**: Shows 5 random audio clips initially with option to view all
- **Audio Player**: Built-in audio player with playback controls and volume adjustment
- **Google Transcription**: Get transcriptions for all audio clips using Google Speech-to-Text
- **Cloud Storage**: Save audio clips to Google Cloud Storage and store metadata in database
- **Progress Tracking**: Visual progress indicator showing current processing step
- **Dark Theme**: Minimalistic dark UI design for better user experience

## Tech Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for styling with custom dark theme
- **Lucide React** for icons
- **Radix UI** components for accessibility
- **Axios** for API communication

### Backend
- **FastAPI** with Python
- **SQLAlchemy** for database operations
- **Google Cloud Speech-to-Text** for transcription
- **Google Cloud Storage** for file storage
- **yt-dlp** for YouTube video downloading
- **PyDub** and **webrtcvad** for audio processing

## Getting Started

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- Google Cloud credentials configured
- PostgreSQL database

### Frontend Setup

1. Navigate to the client directory:
```bash
cd client
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Usage

1. **Enter YouTube URL**: Paste a YouTube video URL in the input field
2. **Process Video**: Click "Process Video" to download and split the audio
3. **Preview Clips**: Listen to 5 random audio clips or view all clips
4. **Get Transcriptions**: Click "Get Transcriptions" to transcribe all clips
5. **Save to Cloud**: Click "Save to Cloud & Database" to store everything

## Project Structure

```
├── client/                 # Frontend React application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── lib/           # Utilities and API functions
│   │   └── App.tsx        # Main application component
│   ├── package.json
│   └── tailwind.config.js
├── server/                # Backend FastAPI application  
│   ├── app/
│   │   ├── core/         # Configuration and database
│   │   ├── models/       # Database models
│   │   ├── routes/       # API endpoints
│   │   ├── services/     # Business logic
│   │   └── schemas/      # Pydantic schemas
│   ├── output/           # Generated audio clips
│   │   └── completed/    # Completed videos (moved after processing)
│   └── requirements.txt
└── README.md
```

## Audio Clip Organization

The system organizes audio clips in two locations:

- **`output/<video_id>/`** - Active processing folder
  - Contains audio clips during processing
  - Includes metadata files (`clip_metadata.json`, `video_metadata.json`)
  - Used for transcription and cloud storage operations

- **`output/completed/<video_id>/`** - Completed videos
  - Videos are automatically moved here after successful cloud storage
  - Preserves all files and metadata for future reference
  - Keeps active folder clean

## API Endpoints

- `POST /api/v1/split-audio` - Split YouTube video into audio clips
- `POST /api/v1/transcribe-clips` - Transcribe audio clips
- `POST /api/v1/save-clips` - Save clips to cloud storage and database
- `GET /output/{video_id}/{clip_name}` - Serve audio files

## Environment Variables

Create a `.env` file in the server directory:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GCP_BUCKET_NAME=your-bucket-name
APP_NAME=Audio Processor
DEBUG=true
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.