"""
Prompt Templates
----------------
Centralized repository for all AI prompts used across Cinema OS.
This module provides consistent, reusable prompts for story generation, scene breakdown,
and other AI-powered features. Centralizing prompts makes them easier to maintain and optimize.
"""

from config.settings import DEFAULT_NUM_STORIES


class PromptTemplates:
    """
    Collection of prompt templates for various AI operations.
    These templates are designed to produce consistent, high-quality outputs across
    different AI models and use cases throughout the application.
    """
    
    @staticmethod
    def story_generation_prompt(user_idea, num_stories=DEFAULT_NUM_STORIES):
        """
        Generate a prompt for creating multiple story variations.
        This prompt guides the AI to create diverse, well-structured story concepts
        with different narrative approaches while maintaining creative coherence.
        
        Args:
            user_idea: The user's original story concept
            num_stories: Number of variations to generate
            
        Returns:
            str: Formatted prompt for story generation
        """
        return f"""Based on this story idea: "{user_idea}"

Generate {num_stories} different story variations. Each variation should have:
- A unique, compelling title (5-8 words)
- A 2-3 sentence description that captures the essence
- An estimated number of scenes (between 3-8 scenes)

Make each variation creatively different by exploring:
- Different tones (dramatic, comedic, thriller, heartwarming, etc.)
- Different perspectives (protagonist viewpoint, antagonist, observer, etc.)
- Different narrative approaches (linear, non-linear, parallel stories, etc.)

Return ONLY a valid JSON array in this exact format:
[
  {{"title": "Story Title", "description": "Story description", "scenes": 5}},
  {{"title": "Another Title", "description": "Another description", "scenes": 6}}
]

Do not include any additional text or explanations."""
    
    
    @staticmethod
    def story_generation_system_prompt():
        """
        System prompt for story generation model.
        This sets the AI's persona and behavior guidelines to ensure consistent,
        creative outputs that align with Cinema OS's storytelling goals.
        
        Returns:
            str: System prompt for story generation
        """
        return """You are a creative storytelling AI assistant for Cinema OS, a professional story production studio.

Your role is to:
- Generate diverse, engaging story concepts from user ideas
- Create variations that explore different creative directions
- Provide structured, production-ready story outlines
- Balance creativity with practical production considerations

Guidelines:
- Keep titles concise and memorable
- Write descriptions that capture emotional hooks
- Estimate scene counts realistically for video production
- Ensure each variation is distinctly different
- Use clear, professional language"""
    
    
    @staticmethod
    def rag_system_prompt():
        """
        System prompt for RAG chatbot interactions.
        This guides the AI to provide helpful, accurate answers based on uploaded
        documents while maintaining context and citing sources appropriately.
        
        Returns:
            str: System prompt for RAG interactions
        """
        return """You are a helpful AI assistant for Cinema OS, designed to answer questions based on uploaded documents.

Your responsibilities:
- Answer questions accurately using only the information from uploaded files
- Cite specific sources when providing information
- Admit when information is not available in the documents
- Help users plan their story projects using their own research materials

Guidelines:
- Be concise but thorough
- Use professional, friendly language
- Always ground answers in the provided documents
- If asked about information not in documents, politely state that"""
    
    
    @staticmethod
    def scene_breakdown_prompt(story_description):
        """
        Generate a prompt for breaking down a story into scenes.
        This will be used in future agent implementation to create detailed
        scene-by-scene breakdowns from selected stories.
        
        Args:
            story_description: The selected story's description
            
        Returns:
            str: Formatted prompt for scene breakdown
        """
        return f"""Based on this story: "{story_description}"

Create a detailed scene-by-scene breakdown. For each scene provide:
- Scene number
- Location/setting
- Time of day
- Key characters present
- Brief action description (2-3 sentences)
- Emotional tone

Format as a JSON array:
[
  {{
    "scene_number": 1,
    "location": "Living room",
    "time": "Afternoon",
    "characters": ["Cat", "Dog"],
    "action": "Description of what happens",
    "tone": "Peaceful then tense"
  }}
]"""
    
    
    @staticmethod
    def image_prompt_generation(scene_description):
        """
        Generate a prompt for creating image generation prompts.
        This will be used by Agent 2 to create detailed image prompts
        from scene descriptions for AI image generation tools.
        
        Args:
            scene_description: Description of a specific scene
            
        Returns:
            str: Formatted prompt for image prompt generation
        """
        return f"""Create a detailed image generation prompt for this scene:
"{scene_description}"

The prompt should:
- Describe visual elements clearly (composition, lighting, colors)
- Specify art style or photographic style
- Include mood and atmosphere details
- Be optimized for AI image generation (Midjourney, DALL-E, Stable Diffusion)

Return a single, detailed prompt string."""
    
    
    @staticmethod
    def video_prompt_generation(scene_description, image_description):
        """
        Generate a prompt for creating video generation prompts.
        This will be used by Agent 3 to create motion and camera prompts
        for AI video generation from static images.
        
        Args:
            scene_description: Description of the scene
            image_description: Description of the generated image
            
        Returns:
            str: Formatted prompt for video prompt generation
        """
        return f"""Create a video generation prompt for this scene:

Scene: "{scene_description}"
Image: "{image_description}"

The video prompt should specify:
- Camera movement (pan, zoom, tilt, static, etc.)
- Subject motion (if any)
- Duration (typically 3-5 seconds)
- Transition style
- Pacing (slow, medium, fast)

Return a concise video prompt optimized for AI video generation tools."""


# Create singleton instance for easy import
# This allows other modules to use: from services.prompt_templates import prompts
prompts = PromptTemplates()
