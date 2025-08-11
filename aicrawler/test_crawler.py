"""
Test script for AICrawler
"""
import sys
from pathlib import Path
import logging
import json

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.core.workflow import CrawlerPipeline
from src.core.storage import DataExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_crawler():
    """Test the crawler with different websites"""
    
    # Test sites
    test_sites = [
        {
            "url": "https://quotes.toscrape.com/",
            "depth": 2,
            "limit": 10,
            "description": "Quotes website (simple structure)"
        },
        {
            "url": "https://httpbin.org/",
            "depth": 1,
            "limit": 5,
            "description": "HTTP testing service"
        },
        {
            "url": "https://example.com/",
            "depth": 1,
            "limit": 3,
            "description": "Example domain"
        }
    ]
    
    pipeline = CrawlerPipeline()
    exporter = DataExporter()
    
    print("=" * 60)
    print("AICrawler Test Script")
    print("=" * 60)
    
    for i, site in enumerate(test_sites, 1):
        print(f"\nTest {i}: {site['description']}")
        print(f"URL: {site['url']}")
        print(f"Depth: {site['depth']}, Limit: {site['limit']}")
        print("-" * 40)
        
        try:
            # Run crawler
            result = pipeline.crawl(
                start_url=site['url'],
                max_depth=site['depth'],
                max_pages=site['limit']
            )
            
            # Print results
            print(f"✓ Successfully crawled {result.total_crawled} pages")
            print(f"✓ Found {sum(len(p.links) for p in result.pages)} total links")
            print(f"✓ Encountered {len(result.errors)} errors")
            
            # Export results
            json_path = exporter.export_to_json(result, f"test_{i}_results.json")
            md_path = exporter.export_to_markdown(result, f"test_{i}_results.md")
            pdf_path = exporter.export_to_pdf(result, f"test_{i}_results.pdf")
            
            print(f"✓ Exported to:")
            print(f"  - JSON: {json_path}")
            print(f"  - Markdown: {md_path}")
            print(f"  - PDF: {pdf_path}")
            
            # Show sample content
            if result.pages:
                page = result.pages[0]
                print(f"\nSample page: {page.title or 'Untitled'}")
                print(f"URL: {page.url}")
                if page.cleaned_content:
                    preview = page.cleaned_content[:200] + "..." if len(page.cleaned_content) > 200 else page.cleaned_content
                    print(f"Content preview: {preview}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("Check 'data/exports' directory for output files.")
    print("=" * 60)


if __name__ == "__main__":
    test_crawler()