# YouTube to Buzzsprout Converter

A web application that allows you to easily convert YouTube videos to podcast episodes and upload them directly to your Buzzsprout podcast.

## Features

- 🎥 **YouTube Integration**: Extract audio and metadata from YouTube videos
- 🎵 **Audio Processing**: Convert videos to high-quality MP3 audio files
- 📝 **Metadata Extraction**: Automatically populate episode details from video information
- ✅ **Confirmation Interface**: Review and edit episode details before uploading
- 🚀 **Buzzsprout Upload**: Seamlessly upload episodes to your Buzzsprout podcast
- 🌐 **Modern Web Interface**: Beautiful, responsive UI built with Bootstrap
- 📊 **Progress Tracking**: Visual progress indicators throughout the conversion process

## Requirements

- Python 3.7+
- FFmpeg (for audio conversion)
- Buzzsprout API credentials

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd youtube-to-buzzsprout
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg:**
   
   **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```
   
   **macOS (with Homebrew):**
   ```bash
   brew install ffmpeg
   ```
   
   **Windows:**
   Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Buzzsprout credentials:
   ```env
   BUZZSPROUT_API_TOKEN=your_api_token_here
   BUZZSPROUT_PODCAST_ID=your_podcast_id_here
   UPLOAD_DIR=./uploads
   ```

## Getting Buzzsprout Credentials

1. **API Token:**
   - Log into your Buzzsprout account
   - Go to Settings → API
   - Generate a new API token
   - Copy the token to your `.env` file

2. **Podcast ID:**
   - In your Buzzsprout dashboard, look at the URL
   - The podcast ID is the number after `/podcasts/`
   - Example: `buzzsprout.com/podcasts/123456` → ID is `123456`

## Usage

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Open your browser and go to:**
   ```
   http://localhost:5000
   ```

3. **Convert a video:**
   - Paste a YouTube video URL
   - Click "Start Processing"
   - Review and edit the auto-filled episode details
   - Click "Upload to Buzzsprout"
   - Your episode is now live on your podcast!

## Workflow

### Step 1: YouTube URL Input
- Paste any valid YouTube video URL
- The system validates the URL format

### Step 2: Metadata Extraction
- Extracts video title, description, uploader, and other metadata
- Retrieves video duration, upload date, and view count

### Step 3: Audio Download
- Downloads the highest quality audio track
- Converts to MP3 format (192 kbps)
- Adds ID3 metadata tags

### Step 4: Confirmation & Editing
- Review auto-populated episode details
- Edit title, description, summary, and tags
- Set episode/season numbers
- Configure publication settings (published, explicit, private)

### Step 5: Buzzsprout Upload
- Creates episode on Buzzsprout
- Uploads audio file
- Displays success page with episode details and sharing options

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BUZZSPROUT_API_TOKEN` | Your Buzzsprout API token | Required |
| `BUZZSPROUT_PODCAST_ID` | Your podcast ID | Required |
| `UPLOAD_DIR` | Directory for temporary audio files | `./uploads` |
| `FLASK_ENV` | Flask environment (`development` or `production`) | `production` |
| `PORT` | Server port | `5000` |
| `HOST` | Server host | `127.0.0.1` (dev) or `0.0.0.0` (prod) |
| `SECRET_KEY` | Flask secret key for sessions | Auto-generated |

### Audio Quality Settings

The application downloads the best available audio quality and converts to MP3 with these settings:
- **Format**: MP3
- **Bitrate**: 192 kbps
- **Sample Rate**: Preserved from source
- **Metadata**: ID3 tags with video information

## File Structure

```
youtube-to-buzzsprout/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── youtube_handler.py     # YouTube video processing
├── buzzsprout_handler.py  # Buzzsprout API integration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── confirm.html
│   └── success.html
└── uploads/              # Temporary audio files (auto-created)
```

## API Endpoints

### Web Routes
- `GET /` - Main application page
- `POST /process` - Process YouTube video
- `POST /upload` - Upload to Buzzsprout
- `GET /episode/<id>` - View episode details
- `GET /history` - View recent episodes

### API Routes
- `GET /api/config-status` - Check Buzzsprout configuration
- `GET /api/test-connection` - Test Buzzsprout API connection

## Troubleshooting

### Common Issues

**"Configuration Error" message:**
- Check your `.env` file exists and has valid credentials
- Verify your Buzzsprout API token is correct
- Ensure your podcast ID is correct

**"Failed to download audio" error:**
- Check that FFmpeg is installed and accessible
- Verify the YouTube URL is valid and accessible
- Some videos may be restricted or unavailable

**Upload fails:**
- Check your internet connection
- Verify Buzzsprout API credentials
- Ensure the audio file isn't too large (500MB limit)

**"yt-dlp" errors:**
- Update yt-dlp: `pip install --upgrade yt-dlp`
- Some videos may require specific extractors

### Debug Mode

Run in debug mode for detailed error messages:
```bash
export FLASK_ENV=development
python app.py
```

## Dependencies

- **Flask**: Web framework
- **yt-dlp**: YouTube video downloading
- **requests**: HTTP client for Buzzsprout API
- **mutagen**: Audio metadata handling
- **validators**: URL validation
- **python-dotenv**: Environment variable management

## Security Notes

- Keep your API credentials secure
- Use HTTPS in production
- Set a strong `SECRET_KEY` for production deployment
- Consider rate limiting for public deployments

## License

This project is open source. Please check the license file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Buzzsprout API documentation
- Check yt-dlp documentation for YouTube-related issues

---

**Happy podcasting! 🎙️**