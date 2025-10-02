import os
import io
from PIL import Image
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class ProfilePictureHandler:
    def __init__(self):
        """Initialize the profile picture handler with Supabase connection."""
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        self.profile_images_dir = os.path.join(os.path.dirname(__file__), 'profile_images')
        self.default_profile_picture = 'default_profile.webp'
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL and API key must be set in environment variables")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Ensure profile images directory exists
        os.makedirs(self.profile_images_dir, exist_ok=True)
        
        # Create default profile picture if it doesn't exist
        self._create_default_profile_picture()
    
    def _create_default_profile_picture(self):
        """Create a default profile picture if it doesn't exist."""
        default_path = os.path.join(self.profile_images_dir, self.default_profile_picture)
        
        if not os.path.exists(default_path):
            # Create a simple default avatar (gray circle with white background)
            size = (200, 200)
            image = Image.new('RGB', size, color='white')
            
            # You can customize this to create a more sophisticated default image
            # For now, we'll create a simple gray circle
            from PIL import ImageDraw
            draw = ImageDraw.Draw(image)
            
            # Draw a gray circle
            margin = 20
            draw.ellipse([margin, margin, size[0] - margin, size[1] - margin], 
                        fill='#CCCCCC', outline='#999999', width=2)
            
            # Save as WebP
            image.save(default_path, 'WEBP', quality=85)
    
    def get_profile_picture_url(self, user_id):
        """
        Get the profile picture URL for a user from the database.
        If no profile picture exists, return the default profile picture.
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            dict: Response with success flag and profile picture filename
        """
        try:
            # Query the database for the user's profile picture URL
            response = self.supabase.table('users').select('ProfilePictureURL').eq('UserID', user_id).execute()
            
            if response.data and len(response.data) > 0:
                profile_url = response.data[0].get('ProfilePictureURL')
                
                if profile_url and profile_url.strip():
                    # Check if the file actually exists
                    profile_path = os.path.join(self.profile_images_dir, profile_url)
                    if os.path.exists(profile_path):
                        return {
                            'success': True,
                            'profile_picture': profile_url,
                            'is_default': False
                        }
                
                # If no profile picture URL or file doesn't exist, return default
                return {
                    'success': True,
                    'profile_picture': self.default_profile_picture,
                    'is_default': True
                }
            else:
                return {
                    'success': False,
                    'message': 'User not found',
                    'profile_picture': self.default_profile_picture,
                    'is_default': True
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving profile picture: {str(e)}',
                'profile_picture': self.default_profile_picture,
                'is_default': True
            }
    
    def save_profile_picture(self, user_id, image_file, max_size=(400, 400), quality=85):
        """
        Save a profile picture for a user, converting it to WebP format.
        
        Args:
            user_id (int): The user's ID
            image_file: File object (from Flask request.files) or PIL Image
            max_size (tuple): Maximum dimensions for the image (width, height)
            quality (int): WebP quality (1-100)
            
        Returns:
            dict: Response with success flag and message
        """
        try:
            # Generate filename based on user ID
            filename = f"user_{user_id}_profile.webp"
            file_path = os.path.join(self.profile_images_dir, filename)
            
            # Handle different input types
            if hasattr(image_file, 'read'):
                # File object from Flask
                image_data = image_file.read()
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_file, str):
                # File path
                image = Image.open(image_file)
            elif isinstance(image_file, Image.Image):
                # PIL Image object
                image = image_file
            else:
                return {
                    'success': False,
                    'message': 'Invalid image file format'
                }
            
            # Convert to RGB if necessary (handles RGBA, P mode, etc.)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image while maintaining aspect ratio
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Make image square by cropping or padding
            image = self._make_square(image, max_size[0])
            
            # Save as WebP
            image.save(file_path, 'WEBP', quality=quality, optimize=True)
            
            # Update database with new profile picture URL
            update_response = self.supabase.table('users').update({
                'ProfilePictureURL': filename
            }).eq('UserID', user_id).execute()
            
            if update_response.data:
                return {
                    'success': True,
                    'message': 'Profile picture saved successfully',
                    'filename': filename,
                    'file_path': file_path
                }
            else:
                # Delete the file if database update failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {
                    'success': False,
                    'message': 'Failed to update database with new profile picture'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error saving profile picture: {str(e)}'
            }
    
    def _make_square(self, image, target_size):
        """
        Make an image square by cropping from the center or padding.
        
        Args:
            image (PIL.Image): The image to make square
            target_size (int): The target width/height
            
        Returns:
            PIL.Image: Square image
        """
        width, height = image.size
        
        if width == height:
            return image.resize((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Crop to square from center
        if width > height:
            # Landscape - crop width
            left = (width - height) // 2
            right = left + height
            cropped = image.crop((left, 0, right, height))
        else:
            # Portrait - crop height
            top = (height - width) // 2
            bottom = top + width
            cropped = image.crop((0, top, width, bottom))
        
        return cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    def delete_profile_picture(self, user_id):
        """
        Delete a user's profile picture file and reset database URL to None.
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            dict: Response with success flag and message
        """
        try:
            # Get current profile picture filename
            response = self.supabase.table('users').select('ProfilePictureURL').eq('UserID', user_id).execute()
            
            if response.data and len(response.data) > 0:
                profile_url = response.data[0].get('ProfilePictureURL')
                
                if profile_url and profile_url != self.default_profile_picture:
                    # Delete the file
                    file_path = os.path.join(self.profile_images_dir, profile_url)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                
                # Update database to remove profile picture URL
                update_response = self.supabase.table('users').update({
                    'ProfilePictureURL': None
                }).eq('UserID', user_id).execute()
                
                if update_response.data:
                    return {
                        'success': True,
                        'message': 'Profile picture deleted successfully'
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Failed to update database'
                    }
            else:
                return {
                    'success': False,
                    'message': 'User not found'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting profile picture: {str(e)}'
            }
    
    def get_profile_picture_path(self, user_id):
        """
        Get the full file path to a user's profile picture.
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            str: Full file path to the profile picture
        """
        result = self.get_profile_picture_url(user_id)
        filename = result.get('profile_picture', self.default_profile_picture)
        return os.path.join(self.profile_images_dir, filename)


# Convenience functions for easy import
def get_user_profile_picture(user_id):
    """Get a user's profile picture URL."""
    handler = ProfilePictureHandler()
    return handler.get_profile_picture_url(user_id)


def save_user_profile_picture(user_id, image_file):
    """Save a user's profile picture."""
    handler = ProfilePictureHandler()
    return handler.save_profile_picture(user_id, image_file)


def delete_user_profile_picture(user_id):
    """Delete a user's profile picture."""
    handler = ProfilePictureHandler()
    return handler.delete_profile_picture(user_id)


def get_user_profile_picture_path(user_id):
    """Get the full file path to a user's profile picture."""
    handler = ProfilePictureHandler()
    return handler.get_profile_picture_path(user_id)
