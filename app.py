"""
Cinema OS - Main Application
-----------------------------
The main entry point for Cinema OS, an AI-powered story production studio.
This application combines Gemini File Search for RAG-based document chat (left)
and OpenAI for creative story generation (right) in a unified interface.
"""

import streamlit as st
from pathlib import Path
from utils.session_state import initialize_session_state
from utils.logger import cinema_logger
from components.rag_chat import render_rag_chat
from components.story_console import render_story_console
from config.constants import APP_NAME, APP_ICON, APP_TAGLINE


def load_css():
    """
    Load custom CSS from external file.
    This function reads the cinema_os_theme.css file and injects it into the app
    for consistent, professional styling across all components.
    """
    css_file = Path("assets/styles/cinema_os_theme.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            cinema_logger.info("Custom CSS loaded successfully")
    else:
        cinema_logger.warning("CSS file not found, using default styles")


def main():
    """
    Main application function.
    Sets up the page configuration, initializes session state, loads custom CSS,
    and renders the two-compartment layout with RAG chat (left) and story generation (right).
    """
    
    # Page configuration
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'About': f"{APP_NAME} - {APP_TAGLINE}"
        }
    )
    
    # Load custom CSS theme
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Application header with gradient animated title
    st.markdown(
        f'<h1 class="cinema-title">{APP_ICON} {APP_NAME}</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p class="tagline">{APP_TAGLINE}</p>',
        unsafe_allow_html=True
    )
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Compartment headers
    header_col1, header_col2 = st.columns(2, gap="large")
    
    with header_col1:
        st.markdown("### 📚 Document Knowledge Base")
        st.markdown("Upload your research files and ask questions")
    
    with header_col2:
        st.markdown("### ✨ Story Generator")
        st.markdown("Transform your ideas into compelling stories")
    
    st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
    
    # Two-compartment layout using columns
    left_col, right_col = st.columns(2, gap="large")
    
    # Left compartment: RAG Chat
    with left_col:
        # Use container for better styling control
        with st.container():
            cinema_logger.info("Rendering RAG chat compartment")
            render_rag_chat()
    
    # Right compartment: Story Console
    with right_col:
        # Use container for better styling control
        with st.container():
            cinema_logger.info("Rendering story console compartment")
            render_story_console()
    
    # Footer
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="footer-text">'
        f'<p>{APP_ICON} <strong>{APP_NAME}</strong> - Powered by Gemini File Search & OpenAI</p>'
        unsafe_allow_html=True
    )


# Application entry point
if __name__ == "__main__":
    cinema_logger.info("Starting Cinema OS application")
    main()
