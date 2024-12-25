"""Text Summarization Web Application

This module provides a Streamlit-based web interface for summarizing content from YouTube videos
and web pages using the Groq API and LangChain framework.
"""

import logging
from typing import Optional, Union
from pathlib import Path

# Third-party imports
import streamlit as st
import validators
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import (
    YoutubeLoader,
    UnstructuredURLLoader
)
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
GEMMA_MODEL = "gemma2-9b-it"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

class TextSummarizer:
    """Handles text summarization operations using LangChain and Groq API."""
    
    def __init__(self, api_key: str):
        """Initialize the summarizer with API key.
        
        Args:
            api_key: Groq API key for authentication
        """
        self.llm = ChatGroq(model=GEMMA_MODEL, groq_api_key=api_key)
        self.prompt = PromptTemplate(
            template="""
            Provide a summary of the following content in 300 words for the below content:
            **Content:** {text}
            """,
            input_variables=["text"]
        )
        
    def extract_youtube_content(self, url: str) -> list[Document]:
        """Extract content from YouTube URL with fallback options.
        
        Args:
            url: YouTube URL
            
        Returns:
            List of Document objects containing the video content
            
        Raises:
            ValueError: If content cannot be extracted
        """
        try:
            # First try with add_video_info=True
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=True,
                language=["en"]
            )
            docs = loader.load()
            if docs:
                logger.info(f"Successfully loaded YouTube content with video info from {url}")
                return docs
                
        except Exception as e:
            logger.warning(f"Failed to load YouTube with video info: {str(e)}")
            
        try:
            # Fallback: try without video info
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False,
                language=["en"]
            )
            docs = loader.load()
            if docs:
                logger.info(f"Successfully loaded YouTube content without video info from {url}")
                return docs
                
        except Exception as e:
            logger.error(f"Failed to load YouTube content: {str(e)}")
            raise ValueError(
                "Could not extract YouTube transcript. Please ensure the video has English subtitles available."
            )
        
        raise ValueError("No content could be extracted from the YouTube video")
        
    def load_content(self, url: str) -> list[Document]:
        """Load content from URL (YouTube or website).
        
        Args:
            url: URL to load content from
            
        Returns:
            List of Document objects containing the loaded content
            
        Raises:
            ValueError: If URL is invalid or content cannot be loaded
        """
        try:
            if "youtube.com" in url or "youtu.be" in url:
                return self.extract_youtube_content(url)
            else:
                loader = UnstructuredURLLoader(
                    urls=[url],
                    ssl_verify=False,
                    headers={"User-Agent": USER_AGENT}
                )
                docs = loader.load()
                if not docs:
                    raise ValueError("No content could be extracted from the URL")
                return docs
                
        except Exception as e:
            logger.error(f"Error loading content from URL {url}: {str(e)}")
            if "youtube.com" in url or "youtu.be" in url:
                raise ValueError(
                    "Failed to load YouTube content. Please ensure:\n"
                    "1. The video exists and is publicly available\n"
                    "2. The video has English subtitles/captions available\n"
                    "3. The URL is correct and accessible"
                )
            else:
                raise ValueError(f"Failed to load content: {str(e)}")

    def generate_summary(self, docs: list[Document]) -> str:
        """Generate summary from documents.
        
        Args:
            docs: List of Document objects to summarize
            
        Returns:
            Generated summary text
            
        Raises:
            ValueError: If summarization fails
        """
        try:
            chain = load_summarize_chain(self.llm, chain_type="stuff", prompt=self.prompt)
            return chain.run(docs)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise ValueError(f"Failed to generate summary: {str(e)}")

def setup_page() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Text Summarization",
        page_icon="🦜",
        layout="wide"
    )
    st.title("Text Summarization From YouTube or Website")
    st.subheader('Summarize URL Content')

def main() -> None:
    """Main application entry point."""
    setup_page()
    
    # Sidebar configuration
    with st.sidebar:
        api_key = st.text_input("Groq API Key", value="", type="password")

    # Main content
    url = st.text_input("URL", label_visibility="collapsed")

    if st.button("Summarize the Content from YouTube or Website"):
        try:
            # Input validation
            if not api_key.strip() or not url.strip():
                st.error("Please provide both API key and URL to get started")
                return
                
            if not validators.url(url):
                st.error("Please enter a valid URL (YouTube video or website)")
                return

            # Initialize summarizer and process content
            summarizer = TextSummarizer(api_key)
            
            with st.spinner("Generating summary, please wait..."):
                docs = summarizer.load_content(url)
                summary = summarizer.generate_summary(docs)
                st.success(summary)
                logger.info("Successfully generated summary")

        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            logger.exception("Unexpected error occurred")
            st.error("An unexpected error occurred. Please try again later.")

if __name__ == "__main__":
    main()