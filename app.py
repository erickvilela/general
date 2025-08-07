import os
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from config import Config
from youtube_handler import YouTubeHandler
from buzzsprout_handler import BuzzsproutHandler

app = Flask(__name__)
app.config.from_object(Config)

# Initialize handlers
youtube_handler = YouTubeHandler()
buzzsprout_handler = BuzzsproutHandler()

@app.route('/')
def index():
    """Main landing page with URL input form."""
    return render_template('index.html')

@app.route('/api/config-status')
def config_status():
    """API endpoint to check Buzzsprout configuration status."""
    try:
        success, result = buzzsprout_handler.test_connection()
        if success:
            return jsonify({
                'success': True,
                'podcast_title': result.get('podcast_title', 'Unknown'),
                'podcast_id': result.get('podcast_id')
            })
        else:
            return jsonify({
                'success': False,
                'error': result
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/process', methods=['POST'])
def process_video():
    """Process YouTube video: extract metadata and download audio."""
    youtube_url = request.form.get('youtube_url', '').strip()
    
    if not youtube_url:
        flash('Please provide a YouTube URL.', 'error')
        return redirect(url_for('index'))
    
    # Validate YouTube URL
    is_valid, message = youtube_handler.validate_youtube_url(youtube_url)
    if not is_valid:
        flash(f'Invalid YouTube URL: {message}', 'error')
        return redirect(url_for('index'))
    
    try:
        # Extract video metadata
        success, metadata = youtube_handler.extract_video_metadata(youtube_url)
        if not success:
            flash(f'Failed to extract video metadata: {metadata}', 'error')
            return redirect(url_for('index'))
        
        # Download audio
        success, audio_file_path = youtube_handler.download_audio(youtube_url)
        if not success:
            flash(f'Failed to download audio: {audio_file_path}', 'error')
            return redirect(url_for('index'))
        
        # Add metadata to audio file
        youtube_handler.add_metadata_to_audio(audio_file_path, metadata)
        
        # Get audio file information
        success, audio_info = youtube_handler.get_audio_info(audio_file_path)
        if not success:
            audio_info = None
        
        # Store data in session for confirmation step
        session['metadata'] = metadata
        session['audio_file'] = audio_file_path
        session['audio_info'] = audio_info
        
        return render_template('confirm.html', 
                             metadata=metadata, 
                             audio_file=audio_file_path,
                             audio_info=audio_info)
        
    except Exception as e:
        flash(f'An error occurred while processing the video: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload_to_buzzsprout():
    """Upload the processed audio and metadata to Buzzsprout."""
    try:
        # Get form data
        episode_data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'summary': request.form.get('summary', '').strip(),
            'artist': request.form.get('artist', '').strip(),
            'tags': request.form.get('tags', '').strip(),
            'published': request.form.get('published') == 'true',
            'explicit': request.form.get('explicit') == 'true',
            'private': request.form.get('private') == 'true'
        }
        
        # Handle optional numeric fields
        episode_number = request.form.get('episode_number', '').strip()
        if episode_number.isdigit():
            episode_data['episode_number'] = int(episode_number)
        
        season_number = request.form.get('season_number', '').strip()
        if season_number.isdigit():
            episode_data['season_number'] = int(season_number)
        
        # Get audio file path from form or session
        audio_file = request.form.get('audio_file') or session.get('audio_file')
        if not audio_file or not os.path.exists(audio_file):
            flash('Audio file not found. Please start over.', 'error')
            return redirect(url_for('index'))
        
        # Validate required fields
        if not episode_data['title']:
            flash('Episode title is required.', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Test Buzzsprout connection first
        success, test_result = buzzsprout_handler.test_connection()
        if not success:
            flash(f'Buzzsprout connection failed: {test_result}', 'error')
            return redirect(request.referrer or url_for('index'))
        
        # Create episode with audio on Buzzsprout
        success, result = buzzsprout_handler.create_episode_with_audio(episode_data, audio_file)
        
        if success:
            episode = result
            
            # Get podcast info for success page
            success, podcast_info = buzzsprout_handler.get_podcast_info()
            if not success:
                podcast_info = None
            
            # Clean up temporary audio file
            try:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
            except:
                pass  # File cleanup is not critical
            
            # Clear session data
            session.pop('metadata', None)
            session.pop('audio_file', None)
            session.pop('audio_info', None)
            
            return render_template('success.html', 
                                 episode=episode, 
                                 podcast_info=podcast_info)
        else:
            flash(f'Failed to upload to Buzzsprout: {result}', 'error')
            return redirect(request.referrer or url_for('index'))
            
    except Exception as e:
        flash(f'An error occurred during upload: {str(e)}', 'error')
        return redirect(request.referrer or url_for('index'))

@app.route('/episode/<int:episode_id>')
def view_episode(episode_id):
    """View details of a specific episode."""
    try:
        success, episode = buzzsprout_handler.get_episode(episode_id)
        if success:
            return render_template('episode_detail.html', episode=episode)
        else:
            flash(f'Episode not found: {episode}', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error retrieving episode: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/history')
def episode_history():
    """View recent episodes."""
    try:
        success, episodes = buzzsprout_handler.list_episodes(limit=20)
        if success:
            return render_template('history.html', episodes=episodes)
        else:
            flash(f'Failed to retrieve episodes: {episodes}', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error retrieving episode history: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/test-connection')
def test_api_connection():
    """API endpoint to test Buzzsprout connection."""
    try:
        success, result = buzzsprout_handler.test_connection()
        return jsonify({
            'success': success,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                          error_code=404, 
                          error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('error.html', 
                          error_code=500, 
                          error_message="Internal server error"), 500

@app.template_filter('urlencode')
def urlencode_filter(s):
    """URL encode filter for templates."""
    if s:
        import urllib.parse
        return urllib.parse.quote_plus(s)
    return s

# Create upload directory on startup
try:
    Config.ensure_upload_dir()
except Exception as e:
    print(f"Warning: Could not create upload directory: {e}")

if __name__ == '__main__':
    # Determine if we're in development or production
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0' if not debug_mode else '127.0.0.1')
    
    print("=== YouTube to Buzzsprout Converter ===")
    print(f"Starting server on {host}:{port}")
    print(f"Debug mode: {debug_mode}")
    print("Make sure your .env file is configured with Buzzsprout credentials!")
    print("=" * 40)
    
    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        threaded=True
    )