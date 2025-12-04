"""
Gemini File Search Service
---------------------------
Handles all interactions with Google's Gemini File Search API for RAG functionality.
Updated for google-genai SDK v1.53.0+
"""

import os
import time
import tempfile
from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from utils.logger import cinema_logger

class GeminiFileSearchService:
    """
    Service class for Gemini File Search API operations.
    Encapsulates RAG functionality: store management, file uploads, and querying.
    """
    
    def __init__(self):
        """
        Initialize the Gemini File Search service.
        """
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_MODEL
        self.is_configured = bool(self.api_key)
        self.client = None
        
        if self.is_configured:
            try:
                # Initialize using the new unified Client
                # We explicitly use 'v1beta' to ensure access to the latest File Search features
                self.client = genai.Client(
                    api_key=self.api_key,
                    http_options={'api_version': 'v1beta'}
                )
                cinema_logger.info("Gemini File Search service initialized successfully (SDK v1.53.0+)")
            except Exception as e:
                cinema_logger.error(f"Failed to initialize Gemini Client: {str(e)}")
                self.is_configured = False
        else:
            cinema_logger.warning("Gemini API key not found - service unavailable")
    
    def create_file_search_store(self, store_name="cinema_os_rag_store"):
        """
        Create a new file search store (corpus) in Gemini.
        """
        if not self.is_configured:
            return None
        
        try:
            cinema_logger.info(f"Creating file search store: {store_name}")
            
            # Create store using the new SDK syntax
            store = self.client.file_search_stores.create(
                config={'display_name': store_name}
            )
            
            # In the new SDK, store.name is the ID (e.g., 'fileSearchStores/xyz...')
            cinema_logger.info(f"File search store created: {store.name}")
            return store.name
            
        except Exception as e:
            cinema_logger.error(f"Failed to create file search store: {str(e)}")
            return None
    
    def upload_files_to_store(self, uploaded_files, store_id):
        """
        Upload files directly to the specified file search store.
        """
        if not self.is_configured:
            return False, "❌ API Key missing", 0
        
        try:
            uploaded_count = 0
            
            for uploaded_file in uploaded_files:
                cinema_logger.info(f"Processing file: {uploaded_file.name}")
                
                # Create a temporary file to upload
                # (The SDK requires a file path, not bytes)
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Use the helper method to upload AND add to store in one go
                    cinema_logger.info(f"Uploading to store {store_id}...")
                    
                    operation = self.client.file_search_stores.upload_to_file_search_store(
                        file=tmp_path,
                        file_search_store_name=store_id,
                        config={'display_name': uploaded_file.name}
                    )
                    
                    # Wait for the operation to complete (Server-side processing)
                    while not operation.done:
                        time.sleep(2)
                        operation = self.client.operations.get(operation)
                        
                    uploaded_count += 1
                    cinema_logger.info(f"File indexed successfully: {uploaded_file.name}")
                    
                finally:
                    # Clean up the local temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            
            return True, f"✅ Successfully indexed {uploaded_count} files", uploaded_count
            
        except Exception as e:
            cinema_logger.error(f"Upload failed: {str(e)}")
            return False, f"❌ Upload failed: {str(e)}", 0
    
    def query_rag(self, question, store_id):
        """
        Query the RAG system using the File Search tool.
        """
        if not self.is_configured:
            return {'answer': None, 'citations': [], 'error': "API Key missing"}
        
        try:
            cinema_logger.info(f"Querying RAG with store: {store_id}")
            
            # Configure the tool with the specific store ID
            tool_config = [
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_id]
                    )
                )
            ]

            # Generate content using the tool
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=question,
                config=types.GenerateContentConfig(
                    tools=tool_config
                )
            )
            
            # Extract Answer
            answer = response.text
            
            # Extract Citations (Grounding Metadata)
            citations = []
            if response.candidates and response.candidates[0].grounding_metadata:
                metadata = response.candidates[0].grounding_metadata
                if metadata.grounding_chunks:
                    for chunk in metadata.grounding_chunks:
                        if chunk.retrieved_context:
                            title = chunk.retrieved_context.title or "Unknown Source"
                            citations.append(title)
            
            # Deduplicate citations
            citations = list(set(citations))
            
            return {
                'answer': answer,
                'citations': citations,
                'error': None
            }
            
        except Exception as e:
            cinema_logger.error(f"RAG query error: {str(e)}")
            return {
                'answer': None,
                'citations': [],
                'error': f"❌ Query error: {str(e)}"
            }

    def delete_store(self, store_id):
        """
        Delete the store to clean up resources.
        """
        if not self.is_configured: 
            return False
            
        try:
            self.client.file_search_stores.delete(name=store_id)
            cinema_logger.info(f"Store deleted: {store_id}")
            return True
        except Exception as e:
            cinema_logger.error(f"Failed to delete store: {str(e)}")
            return False

# Singleton instance
gemini_service = GeminiFileSearchService()