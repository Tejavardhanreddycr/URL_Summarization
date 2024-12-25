"""Text Summarization API

This module provides a FastAPI-based REST API for summarizing content from YouTube videos
and web pages using the Groq API and LangChain framework.
"""

import logging
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, SecretStr
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import YoutubeLoader, UnstructuredURLLoader
from langchain_core.documents import Document
import validators

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
GEMMA_MODEL = "gemma2-9b-it"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

# FastAPI App
app = FastAPI(
    title="Text Summarization API",
    description="Summarize content from YouTube or Website URLs",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SummarizationRequest(BaseModel):
    """Request model for summarization endpoint."""
    groq_api_key: SecretStr = Field(..., description="Groq API key for authentication")
    url: str = Field(..., description="URL to summarize (YouTube or website)")

    class Config:
        json_schema_extra = {
            "example": {
                "groq_api_key": "your-api-key-here",
                "url": "https://www.youtube.com/watch?v=example"
            }
        }

class SummarizationResponse(BaseModel):
    """Response model for summarization endpoint."""
    summary: str = Field(..., description="Generated summary of the content")

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str = Field(..., description="Error message")

class TextSummarizer:
    """Handles text summarization operations using LangChain and Groq API."""
    
    def __init__(self, api_key: str):
        """Initialize the summarizer with API key."""
        self.llm = ChatGroq(model=GEMMA_MODEL, groq_api_key=api_key)
        self.prompt = PromptTemplate(
            template="""
            Provide a summary of the following content in 300 words for the below content:
            **Content:** {text}
            """,
            input_variables=["text"]
        )
    
    def extract_youtube_content(self, url: str) -> list[Document]:
        """Extract content from YouTube URL with fallback options."""
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
            raise HTTPException(
                status_code=400,
                detail="Could not extract YouTube transcript. Please ensure the video has English subtitles available."
            )
        
        raise HTTPException(
            status_code=400,
            detail="No content could be extracted from the YouTube video"
        )
        
    def load_content(self, url: str) -> list[Document]:
        """Load content from URL (YouTube or website)."""
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
                    raise HTTPException(
                        status_code=400,
                        detail="No content could be extracted from the URL"
                    )
                return docs
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error loading content from URL {url}: {str(e)}")
            if "youtube.com" in url or "youtu.be" in url:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Failed to load YouTube content. Please ensure:\n"
                        "1. The video exists and is publicly available\n"
                        "2. The video has English subtitles/captions available\n"
                        "3. The URL is correct and accessible"
                    )
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to load content: {str(e)}"
                )

    async def generate_summary(self, docs: list[Document]) -> str:
        """Generate summary from documents."""
        try:
            chain = load_summarize_chain(self.llm, chain_type="stuff", prompt=self.prompt)
            return chain.run(docs)
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate summary: {str(e)}"
            )

@app.post(
    "/summarize",
    response_model=SummarizationResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def summarize(request: SummarizationRequest) -> Dict[str, str]:
    """
    Summarize content from a YouTube video or webpage.
    
    Args:
        request: SummarizationRequest object containing Groq API key and URL
        
    Returns:
        Dictionary containing the generated summary
        
    Raises:
        HTTPException: If the request is invalid or processing fails
    """
    # Extract and validate inputs
    groq_api_key = request.groq_api_key.get_secret_value().strip()
    url = request.url.strip()

    # Validate inputs
    if not groq_api_key:
        raise HTTPException(status_code=400, detail="API Key is required")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    if not validators.url(url):
        raise HTTPException(status_code=400, detail="Invalid URL provided")

    try:
        # Initialize summarizer
        summarizer = TextSummarizer(groq_api_key)
        
        # Load and summarize content
        docs = summarizer.load_content(url)
        summary = await summarizer.generate_summary(docs)
        
        return {"summary": summary}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error occurred")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
