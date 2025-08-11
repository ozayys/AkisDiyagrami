"""
Storage module for saving crawled data in various formats
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import logging
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import markdown
from ..core.state import CrawlerState, PageContent

logger = logging.getLogger(__name__)


class DataExporter:
    """Handles exporting crawled data to various formats"""
    
    def __init__(self, export_dir: str = "data/exports"):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, prefix: str, extension: str) -> str:
        """Generate a unique filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{extension}"
    
    def export_to_json(self, state: CrawlerState, filename: Optional[str] = None) -> str:
        """Export crawled data to JSON format"""
        if not filename:
            filename = self.generate_filename("crawl_results", "json")
        
        filepath = self.export_dir / filename
        
        # Prepare data for export
        export_data = {
            "metadata": {
                "start_url": state.start_url,
                "max_depth": state.max_depth,
                "max_pages": state.max_pages,
                "total_crawled": state.total_crawled,
                "total_errors": len(state.errors),
                "export_date": datetime.now().isoformat()
            },
            "pages": [
                {
                    "url": page.url,
                    "title": page.title,
                    "cleaned_content": page.cleaned_content,
                    "metadata": page.metadata,
                    "crawled_at": page.crawled_at.isoformat(),
                    "links_count": len(page.links)
                }
                for page in state.pages
            ],
            "errors": state.errors
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported JSON to: {filepath}")
        return str(filepath)
    
    def export_to_markdown(self, state: CrawlerState, filename: Optional[str] = None) -> str:
        """Export crawled data to Markdown format"""
        if not filename:
            filename = self.generate_filename("crawl_results", "md")
        
        filepath = self.export_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# Web Crawl Results\n\n")
            f.write(f"**Start URL:** {state.start_url}\n\n")
            f.write(f"**Crawl Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Pages Crawled:** {state.total_crawled}\n\n")
            f.write(f"**Maximum Depth:** {state.max_depth}\n\n")
            f.write("---\n\n")
            
            # Write page contents
            for i, page in enumerate(state.pages, 1):
                f.write(f"## Page {i}: {page.title or 'Untitled'}\n\n")
                f.write(f"**URL:** [{page.url}]({page.url})\n\n")
                f.write(f"**Crawled At:** {page.crawled_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                if page.metadata.get('description'):
                    f.write(f"**Description:** {page.metadata['description']}\n\n")
                
                f.write("### Content\n\n")
                if page.cleaned_content:
                    # Split content into paragraphs
                    paragraphs = page.cleaned_content.split('\n\n')
                    for para in paragraphs[:10]:  # Limit to first 10 paragraphs
                        if para.strip():
                            f.write(f"{para}\n\n")
                    
                    if len(paragraphs) > 10:
                        f.write(f"*... ({len(paragraphs) - 10} more paragraphs)*\n\n")
                else:
                    f.write("*No content available*\n\n")
                
                f.write("---\n\n")
            
            # Write errors if any
            if state.errors:
                f.write("## Errors\n\n")
                for error in state.errors:
                    f.write(f"- **{error['url']}**: {error['error']}\n")
        
        logger.info(f"Exported Markdown to: {filepath}")
        return str(filepath)
    
    def export_to_pdf(self, state: CrawlerState, filename: Optional[str] = None) -> str:
        """Export crawled data to PDF format"""
        if not filename:
            filename = self.generate_filename("crawl_results", "pdf")
        
        filepath = self.export_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#1a1a1a'),
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#333333'),
            spaceAfter=12
        )
        normal_style = styles['Normal']
        
        # Add title
        elements.append(Paragraph("Web Crawl Results", title_style))
        elements.append(Spacer(1, 12))
        
        # Add metadata
        elements.append(Paragraph(f"<b>Start URL:</b> {state.start_url}", normal_style))
        elements.append(Paragraph(f"<b>Crawl Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Paragraph(f"<b>Total Pages:</b> {state.total_crawled}", normal_style))
        elements.append(Paragraph(f"<b>Maximum Depth:</b> {state.max_depth}", normal_style))
        elements.append(Spacer(1, 20))
        
        # Add page contents
        for i, page in enumerate(state.pages, 1):
            # Page header
            elements.append(Paragraph(f"Page {i}: {page.title or 'Untitled'}", heading_style))
            elements.append(Paragraph(f"<b>URL:</b> {page.url}", normal_style))
            elements.append(Spacer(1, 12))
            
            # Page content
            if page.cleaned_content:
                # Limit content length for PDF
                content = page.cleaned_content[:3000]
                if len(page.cleaned_content) > 3000:
                    content += "... (truncated)"
                
                # Clean content for PDF
                content = content.replace('&', '&amp;')
                content = content.replace('<', '&lt;')
                content = content.replace('>', '&gt;')
                
                elements.append(Paragraph(content, normal_style))
            else:
                elements.append(Paragraph("<i>No content available</i>", normal_style))
            
            elements.append(Spacer(1, 20))
            
            # Add page break after each page except the last
            if i < len(state.pages):
                elements.append(PageBreak())
        
        # Build PDF
        doc.build(elements)
        
        logger.info(f"Exported PDF to: {filepath}")
        return str(filepath)


def save_node(state: CrawlerState) -> CrawlerState:
    """LangGraph node for saving data"""
    exporter = DataExporter()
    
    # Always save as JSON
    json_path = exporter.export_to_json(state)
    
    # Update state with export info
    state.status = "complete"
    if 'exports' not in state.metadata:
        state.metadata['exports'] = {}
    state.metadata['exports']['json'] = json_path
    
    logger.info(f"Data saved. Total pages: {state.total_crawled}")
    return state