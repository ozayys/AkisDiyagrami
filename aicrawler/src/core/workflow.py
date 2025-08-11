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


def should_continue(state: CrawlerState) -> str:
    """Determine if crawling should continue"""
    if state.total_crawled >= state.max_pages:
        logger.info(f"Reached max pages limit: {state.max_pages}")
        return "clean"
    
    if not state.to_visit:
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
            final_state = self.workflow.invoke(initial_state)
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
        
        logger.info(f"Starting crawl with streaming: {start_url}")
        
        # Stream the workflow execution
        try:
            for state in self.workflow.stream(initial_state):
                yield state
        except Exception as e:
            logger.error(f"Workflow streaming error: {str(e)}")
            raise