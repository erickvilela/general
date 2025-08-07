import os
import re
import yt_dlp
import validators
from datetime import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, COMM
from config import Config

class YouTubeHandler:
    """Handle YouTube video processing including metadata extraction and audio download."""
    
    def __init__(self):
        self.config = Config()
        self.config.ensure_upload_dir()
    
    def validate_youtube_url(self, url):
        """Validate if the provided URL is a valid YouTube URL."""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([^&]+)',
            r'(?:https?://)?(?:www\.)?youtu\.be/([^?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([^?]+)',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/([^?]+)'
        ]
        
        if not validators.url(url):
            return False, "Invalid URL format"
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return True, "Valid YouTube URL"
        
        return False, "Not a YouTube URL"
    
    def extract_video_metadata(self, url):
        """Extract metadata from YouTube video without downloading."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                metadata = {
                    'video_id': info.get('id', ''),
                    'title': info.get('title', 'Unknown Title'),
                    'description': info.get('description', ''),
                    'uploader': info.get('uploader', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                    'webpage_url': info.get('webpage_url', url)
                }
                
                # Format upload date
                if metadata['upload_date']:
                    try:
                        date_obj = datetime.strptime(metadata['upload_date'], '%Y%m%d')
                        metadata['formatted_date'] = date_obj.strftime('%Y-%m-%d')
                    except:
                        metadata['formatted_date'] = metadata['upload_date']
                
                # Format duration
                if metadata['duration']:
                    hours = metadata['duration'] // 3600
                    minutes = (metadata['duration'] % 3600) // 60
                    seconds = metadata['duration'] % 60
                    if hours > 0:
                        metadata['formatted_duration'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        metadata['formatted_duration'] = f"{minutes:02d}:{seconds:02d}"
                
                return True, metadata
                
        except Exception as e:
            return False, f"Error extracting metadata: {str(e)}"
    
    def download_audio(self, url, output_filename=None):
        """Download audio from YouTube video."""
        try:
            if not output_filename:
                # Generate filename from video ID
                _, metadata = self.extract_video_metadata(url)
                if metadata:
                    safe_title = re.sub(r'[^\w\s-]', '', metadata['title']).strip()
                    safe_title = re.sub(r'[-\s]+', '-', safe_title)
                    output_filename = f"{metadata['video_id']}_{safe_title}.%(ext)s"
                else:
                    output_filename = "%(id)s_%(title)s.%(ext)s"
            
            output_path = os.path.join(self.config.UPLOAD_DIR, output_filename)
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file (yt-dlp might change the extension)
            base_filename = output_filename.replace('.%(ext)s', '')
            possible_files = [
                os.path.join(self.config.UPLOAD_DIR, f"{base_filename}.mp3"),
                os.path.join(self.config.UPLOAD_DIR, f"{base_filename}.m4a"),
                os.path.join(self.config.UPLOAD_DIR, f"{base_filename}.wav"),
            ]
            
            downloaded_file = None
            for file_path in possible_files:
                if os.path.exists(file_path):
                    downloaded_file = file_path
                    break
            
            if not downloaded_file:
                # Try to find any file with the base name
                for file in os.listdir(self.config.UPLOAD_DIR):
                    if base_filename in file:
                        downloaded_file = os.path.join(self.config.UPLOAD_DIR, file)
                        break
            
            if downloaded_file and os.path.exists(downloaded_file):
                return True, downloaded_file
            else:
                return False, "Downloaded file not found"
                
        except Exception as e:
            return False, f"Error downloading audio: {str(e)}"
    
    def add_metadata_to_audio(self, audio_file_path, metadata):
        """Add metadata tags to the downloaded audio file."""
        try:
            # Load the audio file
            audio = MP3(audio_file_path)
            
            # Add ID3 tags if they don't exist
            if audio.tags is None:
                audio.add_tags()
            
            # Set metadata tags
            audio.tags[TIT2] = TIT2(encoding=3, text=metadata['title'])
            audio.tags[TPE1] = TPE1(encoding=3, text=metadata['uploader'])
            audio.tags[TALB] = TALB(encoding=3, text="YouTube Audio")
            
            if metadata.get('formatted_date'):
                audio.tags[TDRC] = TDRC(encoding=3, text=metadata['formatted_date'])
            
            if metadata.get('description'):
                audio.tags[COMM] = COMM(
                    encoding=3,
                    lang='eng',
                    desc='Description',
                    text=metadata['description'][:200]  # Limit description length
                )
            
            # Save the changes
            audio.save()
            return True, "Metadata added successfully"
            
        except Exception as e:
            return False, f"Error adding metadata: {str(e)}"
    
    def get_audio_info(self, audio_file_path):
        """Get information about the audio file."""
        try:
            audio = MP3(audio_file_path)
            file_size = os.path.getsize(audio_file_path)
            
            info = {
                'file_path': audio_file_path,
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2),
                'duration': audio.info.length if audio.info else 0,
                'bitrate': audio.info.bitrate if audio.info else 0,
                'sample_rate': audio.info.sample_rate if audio.info else 0,
            }
            
            return True, info
            
        except Exception as e:
            return False, f"Error getting audio info: {str(e)}"