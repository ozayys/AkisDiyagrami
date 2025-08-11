"""
Web crawler module for fetching and parsing web pages
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Optional, Tuple
import time
import logging
from ..core.state import PageContent, CrawlerState

logger = logging.getLogger(__name__)


class WebCrawler:
    """Handles web page fetching and link extraction"""
    
    def __init__(self, user_agent: Optional[str] = None):
        self.session = requests.Session()
        if user_agent:
            self.session.headers.update({'User-Agent': user_agent})
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def fetch_page(self, url: str) -> Optional[PageContent]:
        """Fetch a single page and extract its content"""
        try:
            # Add delay to be respectful
            time.sleep(0.5)
            
            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = None
            if soup.title:
                title = soup.title.string
            
            # Extract all links
            links = self._extract_links(soup, url)
            
            # Create page content
            page = PageContent(
                url=response.url,  # Use final URL after redirects
                title=title,
                raw_html=response.text,
                links=links,
                metadata={
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': len(response.content)
                }
            )
            
            logger.info(f"Successfully fetched: {url}")
            return page
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {str(e)}")
            return None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all valid links from the page"""
        links = []
        
        for tag in soup.find_all(['a', 'link']):
            href = tag.get('href')
            if href:
                # Convert relative URLs to absolute
                absolute_url = urljoin(base_url, href)
                
                # Parse and validate URL
                parsed = urlparse(absolute_url)
                
                # Only include HTTP(S) links
                if parsed.scheme in ['http', 'https']:
                    # Remove fragment
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if parsed.query:
                        clean_url += f"?{parsed.query}"
                    
                    links.append(clean_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links


def fetch_node(state: dict) -> dict:
    """LangGraph node for fetching web pages"""
    crawler = WebCrawler()
    
    # Initialize with start URL if needed
    if not state.get('to_visit', []) and state.get('total_crawled', 0) == 0:
        state['to_visit'] = state.get('to_visit', [])
        state['to_visit'].append((state['start_url'], 0))
    
    # Ensure visited_urls is a set (it might come as a list from model_dump)
    if 'visited_urls' in state:
        if isinstance(state['visited_urls'], list):
            state['visited_urls'] = set(state['visited_urls'])
    else:
        state['visited_urls'] = set()
    
    # Initialize pages and errors if not exists
    if 'pages' not in state:
        state['pages'] = []
    if 'errors' not in state:
        state['errors'] = []
    
    # Process pages in the queue
    while state.get('to_visit', []) and state.get('total_crawled', 0) < state.get('max_pages', 10):
        url, depth = state['to_visit'].pop(0)
        
        # Skip if already visited
        if url in state['visited_urls']:
            continue
        
        # Skip if depth exceeds limit
        if depth > state.get('max_depth', 2):
            continue
        
        # Mark as visited
        state['visited_urls'].add(url)
        
        # Fetch the page
        logger.info(f"Fetching: {url}")
        page = crawler.fetch_page(url)
        
        if page:
            state['pages'].append(page)
            state['total_crawled'] = state.get('total_crawled', 0) + 1
            
            # Add new links to queue if not at max depth
            if depth < state.get('max_depth', 2):
                for link in page.links:
                    if link not in state['visited_urls']:
                        state['to_visit'].append((link, depth + 1))
        else:
            state['errors'].append({
                'url': url,
                'error': 'Failed to fetch page'
            })
    
    state['status'] = "fetching_complete"
    return state