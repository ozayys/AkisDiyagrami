"""
Main LangGraph workflow for the AICrawler
"""
from langgraph.graph import StateGraph, END
from typing import Dict, Any
import logging
from ..core.state import CrawlerState
from ..core.crawler import fetch_node
from ..core.cleaner import clean_node
from ..core.storage import save_node

logger = logging.getLogger(__name__)


def should_continue(state: dict) -> str:
    """Determine if crawling should continue"""
    if state.get('total_crawled', 0) >= state.get('max_pages', 10):
        logger.info(f"Reached max pages limit: {state.get('max_pages')}")
        return "clean"
    
    if not state.get('to_visit', []):
        logger.info("No more URLs to visit")
        return "clean"
    
    return "fetch"


def create_crawler_workflow() -> StateGraph:
    """Create and configure the LangGraph workflow"""
    
    # Create the workflow
    workflow = StateGraph(CrawlerState)
    
    # Add nodes
    workflow.add_node("fetch", fetch_node)
    workflow.add_node("clean", clean_node)
    workflow.add_node("save", save_node)
    
    # Define the flow
    workflow.set_entry_point("fetch")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "fetch",
        should_continue,
        {
            "fetch": "fetch",  # Continue fetching
            "clean": "clean"   # Move to cleaning
        }
    )
    
    # Add regular edges
    workflow.add_edge("clean", "save")
    workflow.add_edge("save", END)
    
    return workflow.compile()


class CrawlerPipeline:
    """High-level interface for the crawler workflow"""
    
    def __init__(self):
        self.workflow = create_crawler_workflow()
    
    def crawl(self, start_url: str, max_depth: int = 2, max_pages: int = 10) -> CrawlerState:
        """Execute the crawling workflow"""
        
        # Create initial state
        initial_state = CrawlerState(
            start_url=start_url,
            max_depth=max_depth,
            max_pages=max_pages
        )
        
        logger.info(f"Starting crawl: {start_url} (depth={max_depth}, limit={max_pages})")
        
        # Run the workflow
        try:
            # Convert to dict for LangGraph
            state_dict = initial_state.model_dump()
            final_state_dict = self.workflow.invoke(state_dict)
            
            # Convert visited_urls back to set if needed
            if 'visited_urls' in final_state_dict and isinstance(final_state_dict['visited_urls'], list):
                final_state_dict['visited_urls'] = set(final_state_dict['visited_urls'])
            
            # Convert back to CrawlerState
            final_state = CrawlerState(**final_state_dict)
            logger.info(f"Crawl completed: {final_state.total_crawled} pages crawled")
            return final_state
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}")
            raise
    
    def get_state_updates(self, start_url: str, max_depth: int = 2, max_pages: int = 10):
        """Execute the crawling workflow with streaming updates"""
        
        # Create initial state
        initial_state = CrawlerState(
            start_url=start_url,
            max_depth=max_depth,
            max_pages=max_pages
        )
        
        logger.info(f"Starting streaming crawl: {start_url}")
        
        # Run the workflow with streaming
        try:
            # Convert to dict for LangGraph
            state_dict = initial_state.model_dump()
            for state in self.workflow.stream(state_dict):
                # Convert visited_urls back to set if needed
                if 'visited_urls' in state and isinstance(state['visited_urls'], list):
                    state['visited_urls'] = set(state['visited_urls'])
                yield state
        except Exception as e:
            logger.error(f"Workflow streaming error: {str(e)}")
            raise