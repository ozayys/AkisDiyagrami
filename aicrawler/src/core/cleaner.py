"""
HTML cleaning module for removing unnecessary content
"""
from bs4 import BeautifulSoup, Comment
import re
from typing import Optional, List, Set
import logging
from ..core.state import CrawlerState, PageContent

logger = logging.getLogger(__name__)


class HTMLCleaner:
    """Cleans HTML content by removing scripts, styles, ads, and other unwanted elements"""
    
    # Tags to completely remove
    REMOVE_TAGS = {
        'script', 'style', 'noscript', 'iframe', 'object', 'embed',
        'applet', 'audio', 'video', 'source', 'track', 'canvas',
        'svg', 'math', 'map', 'area', 'input', 'button', 'select',
        'textarea', 'form', 'fieldset', 'legend', 'datalist', 'output',
        'progress', 'meter', 'details', 'summary', 'dialog'
    }
    
    # Class/ID patterns that typically indicate ads or unwanted content
    AD_PATTERNS = [
        r'ad[-_]?banner', r'ad[-_]?box', r'ad[-_]?container', r'advertisement',
        r'banner[-_]?ad', r'google[-_]?ad', r'sponsored', r'promo[-_]?box',
        r'social[-_]?media', r'share[-_]?buttons', r'cookie[-_]?notice',
        r'popup', r'overlay', r'modal', r'newsletter', r'subscribe',
        r'comment', r'disqus', r'sidebar', r'widget', r'related[-_]?posts'
    ]
    
    def __init__(self):
        self.ad_pattern = re.compile('|'.join(self.AD_PATTERNS), re.IGNORECASE)
    
    def clean_html(self, html: str) -> str:
        """Clean HTML content and extract meaningful text"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove comments
            for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
                comment.extract()
            
            # Remove unwanted tags
            for tag_name in self.REMOVE_TAGS:
                for tag in soup.find_all(tag_name):
                    tag.decompose()
            
            # Remove elements with ad-related classes/IDs
            for element in soup.find_all(attrs={'class': self.ad_pattern}):
                element.decompose()
            for element in soup.find_all(attrs={'id': self.ad_pattern}):
                element.decompose()
            
            # Remove empty tags
            for tag in soup.find_all():
                if not tag.get_text(strip=True):
                    tag.decompose()
            
            # Extract text with proper spacing
            text_parts = []
            for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'td', 'th', 'div', 'article', 'section']):
                text = element.get_text(strip=True)
                if text and len(text) > 20:  # Skip very short text
                    text_parts.append(text)
            
            # Join with proper spacing
            cleaned_text = '\n\n'.join(text_parts)
            
            # Clean up extra whitespace
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
            
            return cleaned_text.strip()
            
        except Exception as e:
            logger.error(f"Error cleaning HTML: {str(e)}")
            return ""
    
    def extract_metadata(self, html: str) -> dict:
        """Extract useful metadata from HTML"""
        metadata = {}
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract meta tags
            for meta in soup.find_all('meta'):
                name = meta.get('name', meta.get('property', ''))
                content = meta.get('content', '')
                
                if name and content:
                    if name in ['description', 'keywords', 'author', 'og:title', 'og:description', 'twitter:title', 'twitter:description']:
                        metadata[name] = content
            
            # Extract structured data if present
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json
                    data = json.loads(script.string)
                    metadata['structured_data'] = data
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
        
        return metadata


def clean_node(state: CrawlerState) -> CrawlerState:
    """LangGraph node for cleaning HTML content"""
    cleaner = HTMLCleaner()
    
    for page in state.pages:
        if page.raw_html and not page.cleaned_content:
            # Clean the HTML
            cleaned_content = cleaner.clean_html(page.raw_html)
            page.cleaned_content = cleaned_content
            
            # Extract additional metadata
            extra_metadata = cleaner.extract_metadata(page.raw_html)
            page.metadata.update(extra_metadata)
            
            logger.info(f"Cleaned content for: {page.url}")
    
    state.status = "cleaning_complete"
    return state