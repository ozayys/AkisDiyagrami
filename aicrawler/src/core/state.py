"""
State definitions for the AICrawler LangGraph workflow
"""
from typing import List, Dict, Set, Optional, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime


class PageContent(BaseModel):
    """Represents content from a crawled page"""
    url: str
    title: Optional[str] = None
    raw_html: str
    cleaned_content: Optional[str] = None
    links: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    crawled_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CrawlerState(BaseModel):
    """Main state for the crawler workflow"""
    # Input parameters
    start_url: str
    max_depth: int = 2
    max_pages: int = 10
    
    # Crawling state
    current_depth: int = 0
    visited_urls: Set[str] = Field(default_factory=set)
    to_visit: List[Tuple[str, int]] = Field(default_factory=list)  # (url, depth)
    
    # Results
    pages: List[PageContent] = Field(default_factory=list)
    errors: List[Dict[str, str]] = Field(default_factory=list)
    
    # Status
    status: str = "initialized"
    total_crawled: int = 0
    
    # Metadata for storing additional information
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def model_dump(self, **kwargs):
        """Override to handle set serialization"""
        data = super().model_dump(**kwargs)
        data['visited_urls'] = list(self.visited_urls)
        return data
    
    @classmethod
    def model_validate(cls, obj):
        """Override to handle set deserialization"""
        if isinstance(obj, dict) and 'visited_urls' in obj:
            obj['visited_urls'] = set(obj['visited_urls'])
        return super().model_validate(obj)