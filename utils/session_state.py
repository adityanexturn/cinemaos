"""
Session State Manager
---------------------
Initializes and manages all Streamlit session state variables.
This ensures consistent state management across the entire application and prevents
KeyError exceptions when accessing session variables.
"""

import streamlit as st
from config.constants import SESSION_KEYS


def initialize_session_state():
    """
    Initialize all session state variables with default values.
    This function is called at app startup to ensure all required state variables exist.
    It uses a safe check to avoid overwriting existing values on page reloads.
    """
    
    # File Search Store ID - stores the Gemini file search store identifier
    # This is used to maintain the RAG context across multiple queries
    if SESSION_KEYS["FILE_SEARCH_STORE_ID"] not in st.session_state:
        st.session_state[SESSION_KEYS["FILE_SEARCH_STORE_ID"]] = None
    
    # Chat History - stores all user-assistant conversation messages
    # Each message is a dict with 'role' (user/assistant) and 'content' keys
    if SESSION_KEYS["CHAT_HISTORY"] not in st.session_state:
        st.session_state[SESSION_KEYS["CHAT_HISTORY"]] = []
    
    # Generated Stories - stores the list of AI-generated story variations
    # Each story is a dict with 'title', 'description', and 'scenes' keys
    if SESSION_KEYS["GENERATED_STORIES"] not in st.session_state:
        st.session_state[SESSION_KEYS["GENERATED_STORIES"]] = []
    
    # Selected Story - stores the user's chosen story for production
    # This is used to pass the selected story to subsequent agent workflows
    if SESSION_KEYS["SELECTED_STORY"] not in st.session_state:
        st.session_state[SESSION_KEYS["SELECTED_STORY"]] = None
    
    # RAG Ready - boolean flag indicating if file processing is complete
    # True means files are uploaded and indexed, ready for chat queries
    if SESSION_KEYS["RAG_READY"] not in st.session_state:
        st.session_state[SESSION_KEYS["RAG_READY"]] = False
    
    # Uploaded Files - tracks currently uploaded files for display
    # Helps manage UI state and prevent duplicate uploads
    if SESSION_KEYS["UPLOADED_FILES"] not in st.session_state:
        st.session_state[SESSION_KEYS["UPLOADED_FILES"]] = []


def reset_rag_state():
    """
    Reset RAG-related session state variables.
    This is useful when users want to start a new RAG session with different files.
    It clears the chat history and file search store while preserving story data.
    """
    st.session_state[SESSION_KEYS["FILE_SEARCH_STORE_ID"]] = None
    st.session_state[SESSION_KEYS["CHAT_HISTORY"]] = []
    st.session_state[SESSION_KEYS["RAG_READY"]] = False
    st.session_state[SESSION_KEYS["UPLOADED_FILES"]] = []


def reset_story_state():
    """
    Reset story generation related session state variables.
    This allows users to start fresh with a new story idea without affecting
    the RAG chat session in the left compartment.
    """
    st.session_state[SESSION_KEYS["GENERATED_STORIES"]] = []
    st.session_state[SESSION_KEYS["SELECTED_STORY"]] = None
