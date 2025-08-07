import os
import requests
import json
from config import Config

class BuzzsproutHandler:
    """Handle Buzzsprout API operations for podcast episode uploads."""
    
    def __init__(self):
        self.config = Config()
        self.api_token = self.config.BUZZSPROUT_API_TOKEN
        self.podcast_id = self.config.BUZZSPROUT_PODCAST_ID
        self.base_url = f"{self.config.BUZZSPROUT_API_BASE}/{self.podcast_id}"
        
        # Set up headers for API requests
        self.headers = {
            'Authorization': f'Token token={self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self):
        """Test the connection to Buzzsprout API."""
        try:
            self.config.validate_buzzsprout_config()
            
            # Test by getting podcast info
            response = requests.get(
                f"{self.base_url}.json",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                podcast_info = response.json()
                return True, {
                    'message': 'Connection successful',
                    'podcast_title': podcast_info.get('title', 'Unknown'),
                    'podcast_id': self.podcast_id
                }
            elif response.status_code == 401:
                return False, "Authentication failed. Check your API token."
            elif response.status_code == 404:
                return False, "Podcast not found. Check your podcast ID."
            else:
                return False, f"API request failed with status {response.status_code}"
                
        except ValueError as e:
            return False, str(e)
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def get_podcast_info(self):
        """Get information about the podcast."""
        try:
            response = requests.get(
                f"{self.base_url}.json",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to get podcast info: {response.status_code}"
                
        except Exception as e:
            return False, f"Error getting podcast info: {str(e)}"
    
    def create_episode(self, episode_data):
        """Create a new episode on Buzzsprout."""
        try:
            # Prepare the episode data payload
            payload = {
                'title': episode_data.get('title', ''),
                'description': episode_data.get('description', ''),
                'summary': episode_data.get('summary', ''),
                'artist': episode_data.get('artist', ''),
                'tags': episode_data.get('tags', ''),
                'published': episode_data.get('published', False),
                'episode_number': episode_data.get('episode_number'),
                'season_number': episode_data.get('season_number'),
                'explicit': episode_data.get('explicit', False),
                'private': episode_data.get('private', False)
            }
            
            # Remove None values
            payload = {k: v for k, v in payload.items() if v is not None and v != ''}
            
            response = requests.post(
                f"{self.base_url}/episodes.json",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                episode = response.json()
                return True, episode
            else:
                error_msg = f"Failed to create episode: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'errors' in error_data:
                        error_msg += f" - {error_data['errors']}"
                except:
                    error_msg += f" - {response.text}"
                return False, error_msg
                
        except Exception as e:
            return False, f"Error creating episode: {str(e)}"
    
    def upload_audio_file(self, episode_id, audio_file_path):
        """Upload audio file to an existing episode."""
        try:
            if not os.path.exists(audio_file_path):
                return False, "Audio file not found"
            
            # Check file size
            file_size = os.path.getsize(audio_file_path)
            if file_size > self.config.MAX_FILE_SIZE:
                return False, f"File too large. Maximum size is {self.config.MAX_FILE_SIZE // (1024*1024)}MB"
            
            # Prepare file upload
            with open(audio_file_path, 'rb') as audio_file:
                files = {
                    'audio_file': (
                        os.path.basename(audio_file_path),
                        audio_file,
                        'audio/mpeg'
                    )
                }
                
                # Remove Content-Type header for file upload
                upload_headers = {
                    'Authorization': f'Token token={self.api_token}'
                }
                
                response = requests.put(
                    f"{self.base_url}/episodes/{episode_id}.json",
                    headers=upload_headers,
                    files=files,
                    timeout=300  # 5 minutes timeout for large files
                )
            
            if response.status_code == 200:
                episode = response.json()
                return True, episode
            else:
                error_msg = f"Failed to upload audio: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'errors' in error_data:
                        error_msg += f" - {error_data['errors']}"
                except:
                    error_msg += f" - {response.text}"
                return False, error_msg
                
        except Exception as e:
            return False, f"Error uploading audio: {str(e)}"
    
    def create_episode_with_audio(self, episode_data, audio_file_path):
        """Create episode and upload audio in one operation."""
        try:
            # First create the episode
            success, result = self.create_episode(episode_data)
            if not success:
                return False, f"Failed to create episode: {result}"
            
            episode = result
            episode_id = episode['id']
            
            # Then upload the audio
            success, upload_result = self.upload_audio_file(episode_id, audio_file_path)
            if not success:
                return False, f"Episode created but audio upload failed: {upload_result}"
            
            return True, upload_result
            
        except Exception as e:
            return False, f"Error creating episode with audio: {str(e)}"
    
    def get_episode(self, episode_id):
        """Get information about a specific episode."""
        try:
            response = requests.get(
                f"{self.base_url}/episodes/{episode_id}.json",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to get episode: {response.status_code}"
                
        except Exception as e:
            return False, f"Error getting episode: {str(e)}"
    
    def list_episodes(self, limit=10):
        """List recent episodes."""
        try:
            params = {'limit': limit}
            response = requests.get(
                f"{self.base_url}/episodes.json",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to list episodes: {response.status_code}"
                
        except Exception as e:
            return False, f"Error listing episodes: {str(e)}"
    
    def update_episode(self, episode_id, episode_data):
        """Update an existing episode."""
        try:
            # Prepare the episode data payload
            payload = {k: v for k, v in episode_data.items() if v is not None and v != ''}
            
            response = requests.put(
                f"{self.base_url}/episodes/{episode_id}.json",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, response.json()
            else:
                error_msg = f"Failed to update episode: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'errors' in error_data:
                        error_msg += f" - {error_data['errors']}"
                except:
                    error_msg += f" - {response.text}"
                return False, error_msg
                
        except Exception as e:
            return False, f"Error updating episode: {str(e)}"
    
    def delete_episode(self, episode_id):
        """Delete an episode."""
        try:
            response = requests.delete(
                f"{self.base_url}/episodes/{episode_id}.json",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 204:
                return True, "Episode deleted successfully"
            else:
                return False, f"Failed to delete episode: {response.status_code}"
                
        except Exception as e:
            return False, f"Error deleting episode: {str(e)}"