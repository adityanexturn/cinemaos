"""
Story Generation Service
------------------------
Handles all interactions with Google Gemini API for creative story generation.
Updated: 
1. Fixed MAX_TOKENS error by maximizing output limit.
2. Added automatic fallback (2.5 -> 1.5) for stability.
3. Disabled safety filters for creative writing.
"""

from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY, GEMINI_CREATIVE_MODEL
from utils.logger import cinema_logger


class StoryGenerationService:
    """
    Service class for Gemini story generation operations.
    """
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_CREATIVE_MODEL
        self.is_configured = bool(self.api_key)
        self.client = None
        
        if self.is_configured:
            try:
                self.client = genai.Client(api_key=self.api_key)
                cinema_logger.info(f"Story Service ready. Primary: {self.model_name}")
            except Exception as e:
                cinema_logger.error(f"Failed to init Gemini Client: {e}")
                self.is_configured = False
    
    def _generate_with_model(self, model_id, prompt, temperature, safety_settings):
        """
        Helper method to generate content with a specific model.
        Returns the response object or None if it crashes.
        """
        try:
            # FIX: We use a hard high limit (8192) so the model doesn't get cut off.
            # We control the actual length via the Prompt text instructions instead.
            response = self.client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=8192,  # <--- CHANGED: Maximize available space
                    safety_settings=safety_settings,
                    system_instruction="You are a professional screenwriter. Write engaging, creative fiction."
                )
            )
            return response
        except Exception as e:
            cinema_logger.warning(f"Model {model_id} error: {e}")
            return None

    def generate_stories(self, story_idea, number_of_variations=3, target_word_count=500, temperature=0.8):
        """
        Generates story variations with robust error handling and fallbacks.
        """
        if not self.is_configured:
            return {'stories': [], 'error': "❌ API Key missing."}
        
        try:
            cinema_logger.info(f"Generating {number_of_variations} variations...")
            stories = []

            # 1. PERMISSIVE SAFETY SETTINGS
            # We allow all content to prevent the model from blocking creative conflict/drama
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

            for i in range(number_of_variations):
                # Prompt instructs length, so we don't need to choke the token limit
                prompt = f"""
                STORY CONTEXT: {story_idea}
                
                TASK: Write Story Variation #{i + 1}
                LENGTH: Approximately {target_word_count} words.
                STYLE: Cinematic, engaging, distinct.
                """

                # --- Attempt 1: Primary Model ---
                cinema_logger.info(f"Variation {i+1}: Trying {self.model_name}...")
                response = self._generate_with_model(self.model_name, prompt, temperature, safety_settings)
                
                story_text = ""
                used_model = self.model_name
                finish_reason = "Unknown"

                # Check if primary succeeded
                if response and response.text:
                    story_text = response.text
                else:
                    # Diagnose failure
                    if response and response.candidates:
                        finish_reason = response.candidates[0].finish_reason
                        # Try to salvage partial text if it exists
                        if hasattr(response.candidates[0].content, 'parts'):
                             parts = response.candidates[0].content.parts
                             if parts:
                                 story_text = parts[0].text
                                 cinema_logger.info(f"⚠️ Recovered partial text from {self.model_name}")

                    # --- Attempt 2: Fallback (if primary failed completely) ---
                    if not story_text:
                        cinema_logger.warning(f"⚠️ {self.model_name} failed. Reason: {finish_reason}. Retrying with fallback...")
                        
                        response_fallback = self._generate_with_model(self.fallback_model, prompt, temperature, safety_settings)
                        
                        if response_fallback and response_fallback.text:
                            story_text = response_fallback.text
                            used_model = self.fallback_model
                            cinema_logger.info(f"✅ Fallback to {self.fallback_model} successful")
                        else:
                            story_text = f"[Error: Both models refused request. Primary Reason: {finish_reason}]"

                # Create story object
                story = {
                    'id': i + 1,
                    'title': f"Story Variation {i + 1} ({used_model})",
                    'content': story_text,
                    'word_count': len(story_text.split()) if story_text else 0,
                    'tokens_used': 0 # Optional metadata
                }
                stories.append(story)

            return {'stories': stories, 'error': None}

        except Exception as e:
            cinema_logger.error(f"CRITICAL ERROR: {str(e)}")
            return {'stories': [], 'error': f"❌ System Error: {str(e)}"}


# Create singleton instance
story_service = StoryGenerationService()