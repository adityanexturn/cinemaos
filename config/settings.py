import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Model Configuration
# -------------------
# Left Compartment: RAG File Search
# We use Flash for speed and high-volume context retrieval
GEMINI_RAG_MODEL = os.getenv("GEMINI_RAG_MODEL", "gemini-1.5-flash")

# Right Compartment: Story Generation
# We use Pro for better creative writing, nuance, and reasoning
GEMINI_CREATIVE_MODEL = os.getenv("GEMINI_CREATIVE_MODEL", "gemini-1.5-pro")

# Default generic model alias (for backward compatibility)
GEMINI_MODEL = GEMINI_RAG_MODEL

# File Upload Settings
MAX_FILES = int(os.getenv("MAX_FILES", 5))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 50))
ALLOWED_FILE_TYPES = ["pdf", "txt", "csv", "docx", "json", "md"]

# Story Generation Settings
DEFAULT_NUM_STORIES = 5
MIN_STORIES = 3
MAX_STORIES = 10
# Gemini tends to be creative, but 0.7 is a good sweet spot for storytelling
DEFAULT_TEMPERATURE = 0.7

# Validate API Keys
if not GEMINI_API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY not found. The application will not function correctly.")