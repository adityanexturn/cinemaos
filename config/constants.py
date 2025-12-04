"""Constants for Cinema OS"""

# App Metadata
APP_NAME = "Cinema OS"
APP_ICON = "🎬"
APP_TAGLINE = "Your AI-Powered Story Production Studio"

# AI Provider Info
# Both sides now use Gemini, just different models or purposes
LEFT_AI_PROVIDER = "Gemini File Search (RAG)"
RIGHT_AI_PROVIDER = "gemini-2.5-flash"

# Session State Keys
SESSION_KEYS = {
    "FILE_SEARCH_STORE_ID": "file_search_store_id",
    "CHAT_HISTORY": "chat_history",
    "GENERATED_STORIES": "generated_stories",
    "SELECTED_STORY": "selected_story",
    "RAG_READY": "rag_ready",
    "UPLOADED_FILES": "uploaded_files",
}

# UI Messages
MESSAGES = {
    "NO_GEMINI_KEY": "⚠️ Gemini API key not configured. The app will not function.",
    # Removed OpenAI specific message since we only use Gemini now
    "FILES_UPLOADED": "✅ Files uploaded successfully!",
    "PROCESSING_FILES": "🔄 Processing files with Gemini File Search...",
    "RAG_READY": "✅ Files processed! You can now ask questions.",
    "NO_FILES": "📁 Please upload files to start chatting.",
    "STORIES_GENERATED": "✅ Stories generated successfully!",
    "NO_IDEA": "⚠️ Please enter your story idea first.",
    "STORY_SELECTED": "✅ Story selected!",
}

# File Types
SUPPORTED_FILE_TYPES = {
    "pdf": "application/pdf",
    "txt": "text/plain",
    "csv": "text/csv",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "json": "application/json",
    "md": "text/markdown",
}