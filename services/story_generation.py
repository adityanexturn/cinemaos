"""
Story Generation Service
------------------------
Handles all interactions with Google Gemini API for creative story generation.
This service transforms user ideas into multiple compelling story variations.
Updated for Gemini 2.5 & Google Gen AI SDK v1.53+
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
            cinema_logger.info(f"Generating {number_of_variations} variations using {self.model_name}...")
            
            stories = []
            
            # Estimate max tokens (approx 1.5 tokens per word is a safe buffer)
            max_tokens_limit = int(target_word_count * 1.5)

            # 1. Define Safety Settings
            # CRITICAL FIX: We set all thresholds to BLOCK_NONE to allow creative freedom.
            # Without this, Gemini 2.5 often returns 'None' for stories with conflict/drama.
            safety_settings = [
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_NONE"
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_NONE"
                ),
            ]
            
            # Generate each variation separately
            for i in range(number_of_variations):
                cinema_logger.info(f"Generating story variation {i + 1}/{number_of_variations}")
                
                # Create a unique prompt for each variation
                prompt = f"""
                STORY IDEA: {story_idea}
                
                TASK: Write a unique story variation based on the idea above.
                VARIATION NUMBER: {i + 1}
                
                REQUIREMENTS:
                - Tone: Cinematic and Engaging
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
                        safety_settings=safety_settings, # Apply the safety fix
                        system_instruction="You are a professional screenwriter and creative storyteller."
                    )
                )
                
                # 2. Extract text with Null Safety
                # CRITICAL FIX: Check if response.text exists before using it
                story_text = response.text if response.text else ""
                
                # If Gemini refused to generate text (rare with BLOCK_NONE, but possible)
                if not story_text:
                    cinema_logger.warning(f"Variation {i+1} returned empty text. Candidate finish reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")
                    story_text = f"[Error: The model was unable to generate Variation {i+1}. It may have been overloaded or triggered a strict filter.]"
                
                # Get token usage safely
                tokens_used = 0
                if hasattr(response, 'usage_metadata') and response.usage_metadata:
                    tokens_used = response.usage_metadata.total_token_count
                
                # Create story object
                story = {
                    'id': i + 1,
                    'title': f"Story Variation {i + 1}",
                    'content': story_text,
                    'word_count': len(story_text.split()), # This is now safe because story_text is guaranteed to be a string
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