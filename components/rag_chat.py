"""
RAG Chat Component (Left Compartment)
--------------------------------------
Handles the left side of Cinema OS interface for RAG-powered document chat.
Users upload files which are processed by Gemini File Search API, then can ask
questions about their documents with intelligent, context-aware responses.
"""

import streamlit as st
from services.gemini_file_search import gemini_service
from utils.file_handler import validate_uploaded_file, get_file_icon, format_file_size
from utils.logger import cinema_logger
from config.settings import MAX_FILES, GEMINI_API_KEY
from config.constants import SESSION_KEYS, MESSAGES


def render_rag_chat():
    """
    Render the left compartment RAG chat interface.
    This component allows users to upload documents and interact with them through
    a conversational AI interface powered by Gemini File Search API.
    """
    
    
    # Check if Gemini API is configured
    # Show warning banner if API key is missing to guide users
    if not GEMINI_API_KEY:
        st.error(MESSAGES["NO_GEMINI_KEY"])
        st.info("💡 Add your `GEMINI_API_KEY` to the `.env` file to enable this feature.")
        return
    
    # Model selection dropdown
    # Allows users to choose which Gemini model to use for RAG
    st.markdown("#### ⚙️ Model Configuration")
    gemini_models = [
        "gemini-2.5-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.0-pro"
    ]
    
    selected_model = st.selectbox(
        "Select Gemini Model",
        options=gemini_models,
        index=0,
        help="Choose the Gemini model for document analysis"
    )
    
    # Update service model if changed
    # This allows dynamic model switching without restarting the app
    if selected_model != gemini_service.model_name:
        gemini_service.model_name = selected_model
        cinema_logger.info(f"Gemini model changed to: {selected_model}")
    
    st.markdown("---")
    
    # File upload section
    # Supports multiple file types for comprehensive document analysis
    st.markdown("#### 📁 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose your files",
        type=["pdf", "txt", "csv", "docx", "json", "md"],
        accept_multiple_files=True,
        help=f"Upload up to {MAX_FILES} files for analysis",
        key="rag_file_uploader"
    )
    
    # Process uploaded files
    # Validates each file and creates a file search store for RAG functionality
    if uploaded_files:
        
        # Display uploaded files with icons and sizes
        # Provides visual feedback about successfully uploaded documents
        st.markdown(f"**Uploaded Files:** {len(uploaded_files)}")
        
        for uploaded_file in uploaded_files:
            icon = get_file_icon(uploaded_file.name)
            size = format_file_size(uploaded_file.size)
            
            # Validate each file before processing
            # Ensures only valid files are sent to Gemini API
            is_valid, error_msg = validate_uploaded_file(uploaded_file)
            
            if is_valid:
                st.markdown(f"{icon} **{uploaded_file.name}** ({size})")
            else:
                st.error(error_msg)
        
        # Process files button
        # Creates file search store and uploads documents to Gemini
        if not st.session_state[SESSION_KEYS["RAG_READY"]]:
            
            if st.button("🔄 Process Files", use_container_width=True, type="primary"):
                
                with st.spinner(MESSAGES["PROCESSING_FILES"]):
                    
                    # Create file search store
                    # This initializes the RAG corpus in Gemini
                    store_id = gemini_service.create_file_search_store()
                    
                    if store_id:
                        # Upload files to the store
                        # Files are automatically chunked and embedded by Gemini
                        success, message, count = gemini_service.upload_files_to_store(
                            uploaded_files, 
                            store_id
                        )
                        
                        if success:
                            st.session_state[SESSION_KEYS["FILE_SEARCH_STORE_ID"]] = store_id
                            st.session_state[SESSION_KEYS["RAG_READY"]] = True
                            st.session_state[SESSION_KEYS["UPLOADED_FILES"]] = [f.name for f in uploaded_files]
                            st.success(MESSAGES["RAG_READY"])
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("❌ Failed to create file search store. Check your API key.")
    
    st.markdown("---")
    
    # Chat interface
    # Only displayed after files are successfully processed
    if st.session_state[SESSION_KEYS["RAG_READY"]]:
        
        st.markdown("#### 💬 Ask Questions")
        st.markdown(f"Chat with your documents using **{selected_model}**")
        
        # Display chat history
        # Shows conversation between user and AI with proper formatting
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state[SESSION_KEYS["CHAT_HISTORY"]]:
                
                if message["role"] == "user":
                    # User messages aligned to right with blue background
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message["content"])
                else:
                    # Assistant messages aligned to left with robot avatar
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(message["content"])
                        
                        # Display citations if available
                        # Shows source documents for transparency
                        if "citations" in message and message["citations"]:
                            with st.expander("📎 Sources"):
                                for citation in message["citations"]:
                                    st.caption(f"• {citation}")
        
        # Chat input
        # Allows users to ask questions about their documents
        user_question = st.chat_input(
            "Ask anything about your documents...",
            key="rag_chat_input"
        )
        
        if user_question:
            
            # Add user message to chat history
            # Maintains conversation context for better UX
            st.session_state[SESSION_KEYS["CHAT_HISTORY"]].append({
                "role": "user",
                "content": user_question
            })
            
            # Query the RAG system
            # Retrieves relevant information and generates answer
            with st.spinner("🔍 Searching documents..."):
                
                store_id = st.session_state[SESSION_KEYS["FILE_SEARCH_STORE_ID"]]
                result = gemini_service.query_rag(user_question, store_id)
                
                if result["error"]:
                    # Display error if query fails
                    st.session_state[SESSION_KEYS["CHAT_HISTORY"]].append({
                        "role": "assistant",
                        "content": result["error"]
                    })
                else:
                    # Add assistant response with citations
                    st.session_state[SESSION_KEYS["CHAT_HISTORY"]].append({
                        "role": "assistant",
                        "content": result["answer"],
                        "citations": result["citations"]
                    })
            
            # Rerun to update chat display
            st.rerun()
        
        # Reset button
        # Allows users to start fresh with new documents
        if st.button("🔄 Reset Chat", use_container_width=True):
            st.session_state[SESSION_KEYS["CHAT_HISTORY"]] = []
            st.session_state[SESSION_KEYS["RAG_READY"]] = False
            st.session_state[SESSION_KEYS["FILE_SEARCH_STORE_ID"]] = None
            st.rerun()
    
    else:
        # Placeholder when no files are uploaded
        # Guides users on what to do next
        if not uploaded_files:
            st.info(MESSAGES["NO_FILES"])
