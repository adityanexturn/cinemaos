"""
RAG Chat Component
------------------
Left compartment UI for document upload and RAG-based chat using Gemini File Search.
"""

import streamlit as st
from services.gemini_file_search import gemini_service
from config.settings import GEMINI_API_KEY, MAX_FILES, MAX_FILE_SIZE_MB
from config.constants import MESSAGES
from utils.logger import cinema_logger
from utils.file_handler import validate_uploaded_file
import time


def render_rag_chat():
    """
    Render the left compartment RAG chat interface.
    Provides document upload, processing visualization, and chat functionality.
    """
    
    # Check if Gemini API is configured
    if not GEMINI_API_KEY:
        st.error(MESSAGES["NO_GEMINI_KEY"])
        st.info("💡 Add your `GEMINI_API_KEY` to the `.env` file to enable this feature.")
        return
    
    # Model Configuration
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
        help="Choose the Gemini model for document analysis",
        key="gemini_model_selector"
    )
    
    # Update service model if changed
    if selected_model != gemini_service.model_name:
        gemini_service.model_name = selected_model
        cinema_logger.info(f"Gemini model changed to: {selected_model}")
    
    st.markdown("---")
    
    # File Upload Section
    st.markdown("#### 📁 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose your files",
        type=["pdf", "txt", "csv", "docx", "json", "md"],
        accept_multiple_files=True,
        help=f"Upload up to {MAX_FILES} files (max {MAX_FILE_SIZE_MB}MB each)",
        key="rag_file_uploader"
    )
    
    # Process Upload Button
    if uploaded_files:
        st.info(f"📎 {len(uploaded_files)} file(s) ready to upload")
        
        if st.button("🚀 Process Documents", use_container_width=True, type="primary"):
            
            # Step 1: Validate files
            with st.spinner("🔍 Validating files..."):
                time.sleep(0.5)  # Brief pause for visual effect
                valid_files = []
                
                for uploaded_file in uploaded_files:
                    is_valid, message = validate_uploaded_file(uploaded_file)
                    if is_valid:
                        valid_files.append(uploaded_file)
                        st.success(f"✓ {uploaded_file.name} validated")
                    else:
                        st.error(message)
                
                if not valid_files:
                    st.error("❌ No valid files to process!")
                    return
            
            # Step 2: Create File Search Store
            with st.spinner("🏗️ Creating file search store..."):
                store_id = gemini_service.create_file_search_store()
                
                if not store_id:
                    st.error("❌ Failed to create file search store")
                    return
                
                st.session_state.rag_store_id = store_id
                st.success(f"✓ Store created: {store_id.split('/')[-1][:20]}...")
                time.sleep(0.5)
            
            # Step 3: Upload and Process Files
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_files = len(valid_files)
            
            for idx, uploaded_file in enumerate(valid_files):
                progress = (idx + 1) / total_files
                
                # Show current file being processed
                status_text.markdown(f"**Processing file {idx + 1}/{total_files}:** `{uploaded_file.name}`")
                
                # Upload phase
                with st.spinner(f"⬆️ Uploading {uploaded_file.name}..."):
                    progress_bar.progress(progress * 0.4)  # 0-40% for upload
                    time.sleep(0.3)
                
                # Chunking phase
                with st.spinner(f"Chunking {uploaded_file.name}..."):
                    progress_bar.progress(progress * 0.6)  # 40-60% for chunking
                    time.sleep(0.4)
                
                # Embedding phase
                with st.spinner(f"Embedding {uploaded_file.name}..."):
                    progress_bar.progress(progress * 0.8)  # 60-80% for embedding
                    time.sleep(0.4)
                
                # Indexing phase
                with st.spinner(f"Indexing {uploaded_file.name}..."):
                    progress_bar.progress(progress * 1.0)  # 80-100% for indexing
                    time.sleep(0.3)
                
                st.success(f"✅ {uploaded_file.name} processed successfully!")
            
            # Step 4: Final Upload (actual API call happens here)
            with st.spinner("🔗 Finalizing document store..."):
                success, message, count = gemini_service.upload_files_to_store(
                    valid_files, 
                    store_id
                )
                
                progress_bar.progress(1.0)
                
                if success:
                    st.session_state.rag_files_uploaded = True
                    st.session_state.uploaded_file_names = [f.name for f in valid_files]
                    status_text.empty()
                    
                    # Success message with file list
                    st.success(f"🎉 {message}")
                    
                    with st.expander("📋 Uploaded Files", expanded=False):
                        for file_name in st.session_state.uploaded_file_names:
                            st.markdown(f"- ✓ `{file_name}`")
                
                else:
                    st.error(message)
                    status_text.empty()
    
    st.markdown("---")
    
    # Chat Interface (only show if files are uploaded)
    if st.session_state.get('rag_files_uploaded'):
        st.markdown("#### 💬 Ask Questions")
        
        # Show uploaded files info
        with st.expander("📚 Knowledge Base", expanded=False):
            st.markdown(f"**Store ID:** `{st.session_state.rag_store_id.split('/')[-1]}`")
            st.markdown(f"**Files:** {len(st.session_state.uploaded_file_names)}")
            for file_name in st.session_state.uploaded_file_names:
                st.markdown(f"- `{file_name}`")
        
        # Chat input
        user_question = st.text_input(
            "Ask a question about your documents",
            placeholder="What is the main topic of these documents?",
            key="rag_question_input"
        )
        
        if st.button("🔍 Ask", use_container_width=True, type="primary"):
            if not user_question.strip():
                st.warning("Please enter a question!")
            else:
                # Query with visual feedback
                with st.spinner("Searching documents and generating answer..."):
                    
                    # Show search steps
                    search_status = st.empty()
                    
                    search_status.info("Searching relevant chunks...")
                    time.sleep(0.5)
                    
                    search_status.info("Analyzing context...")
                    time.sleep(0.5)
                    
                    search_status.info("Generating answer...")
                    
                    result = gemini_service.query_rag(
                        question=user_question,
                        store_id=st.session_state.rag_store_id
                    )
                    
                    search_status.empty()
                
                # Display results
                if result['error']:
                    st.error(result['error'])
                else:
                    # Answer
                    st.markdown("#### 💡 Answer")
                    st.markdown(
                        f"""
                        <div style="
                            background: linear-gradient(145deg, #1e2533 0%, #1a1f2e 100%);
                            padding: 20px;
                            border-radius: 12px;
                            border-left: 4px solid #34d399;
                            margin: 10px 0;
                        ">
                            <p style="color: #e5e7eb; line-height: 1.8;">
                                {result['answer']}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    # Citations
                    if result['citations']:
                        st.markdown("#### 📚 Sources")
                        for citation in result['citations']:
                            st.markdown(f"- 🔗 {citation}")
                    
                    # Save to chat history
                    if 'rag_chat_history' not in st.session_state:
                        st.session_state.rag_chat_history = []
                    
                    st.session_state.rag_chat_history.append({
                        'question': user_question,
                        'answer': result['answer'],
                        'citations': result['citations']
                    })
        
        # Chat History
        if st.session_state.get('rag_chat_history'):
            st.markdown("---")
            st.markdown("#### 📜 Chat History")
            
            for idx, chat in enumerate(reversed(st.session_state.rag_chat_history)):
                with st.expander(f"Q: {chat['question'][:50]}...", expanded=(idx == 0)):
                    st.markdown(f"**Question:** {chat['question']}")
                    st.markdown(f"**Answer:** {chat['answer']}")
                    if chat['citations']:
                        st.markdown("**Sources:** " + ", ".join(chat['citations']))
    
    else:
        st.info("📤 Upload and process documents to start asking questions!")
    
    # Clear/Reset button
    if st.session_state.get('rag_files_uploaded'):
        st.markdown("---")
        if st.button("🗑️ Clear All & Start Over", use_container_width=True):
            # Delete store
            if st.session_state.get('rag_store_id'):
                gemini_service.delete_store(st.session_state.rag_store_id)
            
            # Clear session state
            st.session_state.rag_files_uploaded = False
            st.session_state.rag_store_id = None
            st.session_state.uploaded_file_names = []
            st.session_state.rag_chat_history = []
            
            st.success("✓ Cleared! Upload new documents to start.")
            st.rerun()
