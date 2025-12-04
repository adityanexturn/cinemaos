"""
Story Generation Service
------------------------
Handles all interactions with Google Gemini API for creative story generation.
This service transforms user ideas into multiple compelling story variations.
"""

from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY, GEMINI_CREATIVE_MODEL
from utils.logger import cinema_logger


class StoryGenerationService:
    """
    Service class for Gemini story generation operations.
    Generates multiple story variations from a single prompt.
    """
    
    def __init__(self):
        """
        Initialize the Story Generation service with Gemini API configuration.
        """
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_CREATIVE_MODEL
        self.is_configured = bool(self.api_key)
        self.client = None
        
        if self.is_configured:
            try:
                # Initialize the unified Gemini Client
                self.client = genai.Client(api_key=self.api_key)
                cinema_logger.info(f"Story Generation service initialized (Model: {self.model_name})")
            except Exception as e:
                cinema_logger.error(f"Failed to initialize Gemini client: {str(e)}")
                self.is_configured = False
        else:
            cinema_logger.warning("Gemini API key not found - service unavailable")
    
    
    def generate_stories(self, story_idea, number_of_variations=3, target_word_count=500, temperature=0.8):
        """
        Generate multiple story variations from a single idea.
        
        Args:
            story_idea: The user's story concept/idea
            number_of_variations: Number of different story versions to generate
            target_word_count: Approximate length target
            temperature: Creativity level (0.0 to 2.0)
            
        Returns:
            dict: {
                'stories': list of story dicts,
                'error': error message if failed
            }
        """
        
        if not self.is_configured:
            return {
                'stories': [],
                'error': "❌ Gemini API key not configured. Please add your API key to .env file."
            }
        
        try:
            cinema_logger.info(f"Generating {number_of_variations} variations for: {story_idea[:50]}...")
            
            stories = []
            
            # Estimate max tokens based on word count (approx 1.3 tokens per word) + buffer
            max_tokens_limit = int(target_word_count * 1.5)
            
            # Generate each variation separately
            for i in range(number_of_variations):
                cinema_logger.info(f"Generating story variation {i + 1}/{number_of_variations}")
                
                # Create a unique prompt for each variation to ensure diversity
                prompt = f"""
                STORY IDEA: {story_idea}
                
                TASK: Write a unique story variation based on the idea above.
                VARIATION NUMBER: {i + 1}
                
                REQUIREMENTS:
                - Tone: Engaging and Cinematic
                - Structure: Clear beginning, middle, and end
                - Length: Approximately {target_word_count} words
                - Make this version distinct from a standard interpretation.
                
                STORY:
                """

                # Call Gemini API
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens_limit,
                        system_instruction="You are a professional screenwriter and creative storyteller. Your goal is to take simple ideas and turn them into compelling narratives."
                    )
                )
                
                # Extract text
                story_text = response.text
                
                # Get token usage if available (handle safely)
                tokens_used = 0
                if response.usage_metadata:
                    tokens_used = response.usage_metadata.total_token_count
                
                # Create story object
                story = {
                    'id': i + 1,
                    'title': f"Story Variation {i + 1}",
                    'content': story_text,
                    'word_count': len(story_text.split()),
                    'tokens_used': tokens_used
                }
                
                stories.append(story)
                cinema_logger.info(f"Story {i + 1} generated successfully ({story['word_count']} words)")
            
            cinema_logger.info(f"All {number_of_variations} stories generated successfully")
            
            return {
                'stories': stories,
                'error': None
            }
            
        except Exception as e:
            cinema_logger.error(f"Story generation failed: {str(e)}")
            return {
                'stories': [],
                'error': f"❌ Generation failed: {str(e)}"
            }


# Create singleton instance
story_service = StoryGenerationService()