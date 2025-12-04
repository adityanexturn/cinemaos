"""
Story Console Component
-----------------------
Right compartment UI for story generation using Google Gemini.
Allows users to input ideas and generate multiple story variations.
"""

import streamlit as st
from services.story_generation import story_service
from config.settings import GEMINI_API_KEY, GEMINI_CREATIVE_MODEL
from config.constants import MESSAGES
from utils.logger import cinema_logger


def render_story_console():
    """
    Render the right compartment story generation interface.
    Provides controls for story generation and displays results.
    """
    
    # Check if Gemini API is configured
    if not GEMINI_API_KEY:
        st.error(MESSAGES["NO_GEMINI_KEY"])
        st.info("💡 Add your `GEMINI_API_KEY` to the `.env` file to enable this feature.")
        return
    
    # Model Configuration
    st.markdown("#### ⚙️ Model Configuration")
    
    # Gemini Models suited for creative writing
    gemini_models = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-2.0-flash-exp" # Experimental if available
    ]
    
    # Attempt to find the default model index
    default_index = 0
    if GEMINI_CREATIVE_MODEL in gemini_models:
        default_index = gemini_models.index(GEMINI_CREATIVE_MODEL)
    
    selected_model = st.selectbox(
        "Select Gemini Model",
        options=gemini_models,
        index=default_index,
        help="Choose the Gemini model for story generation. 'Pro' is better for creativity, 'Flash' for speed.",
        key="story_model_selector"
    )
    
    # Update service model if changed
    if selected_model != story_service.model_name:
        story_service.model_name = selected_model
        cinema_logger.info(f"Gemini model changed to: {selected_model}")
    
    st.markdown("---")
    
    # Story Input Section
    st.markdown("#### ✍️ Your Story Idea")
    
    story_idea = st.text_area(
        "Enter your story concept or idea",
        placeholder="Example: A detective cat solves mysteries in a cyberpunk city...",
        height=150,
        key="story_idea_input",
        help="Describe your story idea in detail. The more context you provide, the better the stories!"
    )
    
    st.markdown("---")
    
    # Generation Settings
    st.markdown("#### 🎛️ Generation Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_variations = st.number_input(
            "Number of Variations",
            min_value=1,
            max_value=5, # Gemini limits might be tighter on rate limits, safe to cap at 5
            value=3,
            step=1,
            help="How many different story versions to generate",
            key="num_variations"
        )
    
    with col2:
        temperature = st.slider(
            "Creativity Level",
            min_value=0.0,
            max_value=2.0,
            value=0.8,
            step=0.1,
            help="Higher values = more creative/random. Lower values = more focused/deterministic",
            key="temperature_slider"
        )
    
    max_words = st.slider(
        "Target Word Count",
        min_value=100,
        max_value=1000,
        value=500,
        step=50,
        help="Approximate length of each story.",
        key="max_words_slider"
    )
    
    st.markdown("---")
    
    # Generate Stories Button
    if st.button("🎬 Generate Stories", use_container_width=True, type="primary"):
        if not story_idea.strip():
            st.error(MESSAGES["NO_IDEA"])
        else:
            # Generate stories
            with st.spinner(f"🎬 Generating {num_variations} story variations with Gemini..."):
                result = story_service.generate_stories(
                    story_idea=story_idea,
                    number_of_variations=num_variations,
                    target_word_count=max_words,
                    temperature=temperature
                )
            
            # Check for errors
            if result['error']:
                st.error(result['error'])
            else:
                # Store stories in session state
                st.session_state.generated_stories = result['stories']
                st.success(MESSAGES["STORIES_GENERATED"])
    
    st.markdown("---")
    
    # Display Generated Stories
    if st.session_state.get('generated_stories'):
        st.markdown("### 📚 Generated Story Variations")
        
        for story in st.session_state.generated_stories:
            # Story Card
            with st.container():
                st.markdown(f"#### 📖 {story['title']}")
                st.caption(f"🔢 {story['word_count']} words")
                
                # Show preview (first 250 characters)
                preview = story['content'][:250] + "..." if len(story['content']) > 250 else story['content']
                st.markdown(preview)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📖 View Full", key=f"view_{story['id']}", use_container_width=True):
                        st.session_state.viewing_story = story
                        st.rerun()
                
                with col2:
                    if st.button("✅ Select", key=f"select_{story['id']}", use_container_width=True):
                        st.session_state.selected_story = story
                        st.success(MESSAGES["STORY_SELECTED"])
                        st.rerun() # Rerun to update the selection indicator immediately
                
                with col3:
                    # Simple copy hack for Streamlit
                    if st.button("📋 Copy", key=f"copy_{story['id']}", use_container_width=True):
                         st.code(story['content'], language="markdown")
                
                st.markdown("---")
    
    # Full Story Viewer (Modal-style)
    if st.session_state.get('viewing_story'):
        story = st.session_state.viewing_story
        
        st.markdown("---")
        st.markdown(f"### 📖 {story['title']} (Full Story)")
        st.caption(f"🔢 {story['word_count']} words")
        
        # Full story content in a styled container
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(145deg, #1e2533 0%, #1a1f2e 100%);
                padding: 20px;
                border-radius: 12px;
                border-left: 4px solid #ee5a6f;
                margin: 10px 0;
            ">
                <p style="color: #e5e7eb; line-height: 1.8; font-size: 1.05rem;">
                    {story['content'].replace(chr(10), '<br><br>')}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Close button
        if st.button("✖ Close Full View", key="close_viewer", use_container_width=True):
            st.session_state.viewing_story = None
            st.rerun()
        
        st.markdown("---")
    
    # Selected Story Indicator
    if st.session_state.get('selected_story'):
        selected = st.session_state.selected_story
        
        st.info(f"✅ Currently Selected: **{selected['title']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👁️ View Selected", key="view_selected"):
                st.session_state.viewing_story = selected
                st.rerun()
        with col2:
            if st.button("🗑️ Deselect", key="deselect"):
                st.session_state.selected_story = None
                st.rerun()