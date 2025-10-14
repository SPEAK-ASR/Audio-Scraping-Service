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
- **FFmpeg** (required for audio processing)
- Google Cloud credentials configured
- PostgreSQL database
- `dos2unix` utility (for fixing line ending issues on Windows/WSL)

#### Installing FFmpeg

**On Linux/WSL:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**On macOS:**
```bash
brew install ffmpeg
```

**On Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add FFmpeg to your system PATH
- Or use WSL (recommended for this project)

### Platform Compatibility

⚠️ **Important:** This application is optimized for **Linux/Unix environments**. 

- **Linux/WSL (Recommended)**: Full compatibility, all features work as expected
- **macOS**: Should work with minimal issues
- **Windows (Native)**: May require modifications:
  - Shell scripts won't work directly (use WSL or Git Bash)
  - Path separators need adjustment in some configurations
  - Virtual environment activation command differs (`.venv\Scripts\activate`)
  
**For Windows users**, we strongly recommend using **WSL (Windows Subsystem for Linux)** for the best experience.

### Verify Installation

Before proceeding, verify all prerequisites are installed:

```bash
# Check Node.js
node --version

# Check npm
npm --version

# Check Python
python3 --version

# Check FFmpeg
ffmpeg -version

# Check dos2unix (if on WSL/Linux)
dos2unix --version
```

All commands should return version numbers without errors.

### Quick Start (Recommended)

The easiest way to get started is using the provided shell scripts:

#### Option 1: Install and Start (First Time)
```bash
./install.sh
```
This script will:
- Check prerequisites (Node.js, Python 3, npm)
- Install all client dependencies
- Create Python virtual environment
- Install all server dependencies
- Start both client and server automatically

#### Option 2: Start Services (After Installation)
```bash
./start.sh
```
Use this when dependencies are already installed. It will:
- Verify dependencies are installed
- Start the FastAPI server on port 8000
- Start the Vite dev server on port 5173
- Display logs location and service URLs

**Note:** Both services will run concurrently. Press `Ctrl+C` to stop both services.

#### Troubleshooting: "Cannot find start.sh" or Permission Errors

If you encounter errors like:
- `bash: ./start.sh: No such file or directory`
- `bash: ./install.sh: /bin/bash^M: bad interpreter`
- Permission denied errors

This is due to Windows-style line endings (CRLF) instead of Unix-style (LF). Fix it with:

```bash
# Install dos2unix if not already installed
sudo apt-get update && sudo apt-get install dos2unix

# Convert the scripts
dos2unix install.sh
dos2unix start.sh

# Make scripts executable
chmod +x install.sh start.sh

# Now run the script
./install.sh
```

### Manual Setup (Alternative)

If you prefer to run services separately or need more control:

#### Frontend Setup

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

#### Backend Setup

1. Navigate to the server directory:
```bash
cd server
```

2. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows WSL/Linux
# On Windows PowerShell: .venv\Scripts\activate
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

**Note:** When running manually, you'll need to open two separate terminals - one for the frontend and one for the backend.

## Service URLs

When running the application, the following services will be available:

- **Frontend (Client)**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **API Redoc**: http://localhost:8000/redoc

## Logs

When using shell scripts, logs are automatically created in the `logs/` directory:
- `logs/client.log` - Vite development server logs
- `logs/server.log` - FastAPI server logs

You can monitor logs in real-time:
```bash
# Watch client logs
tail -f logs/client.log

# Watch server logs
tail -f logs/server.log
```

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