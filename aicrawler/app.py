"""
AICrawler - Streamlit Web Interface
"""
import streamlit as st
import sys
from pathlib import Path
import json
import time
from datetime import datetime
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.core.workflow import CrawlerPipeline
from src.core.storage import DataExporter
from src.core.state import CrawlerState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AICrawler - Web İçerik Toplama",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .error-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'crawl_results' not in st.session_state:
    st.session_state.crawl_results = None
if 'is_crawling' not in st.session_state:
    st.session_state.is_crawling = False


def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🕷️ AICrawler</h1>
        <p>LangGraph Tabanlı Akıllı Web İçerik Toplama ve Temizleme Sistemi</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Crawl Ayarları")
        
        # URL input
        url = st.text_input(
            "🌐 Başlangıç URL'i",
            placeholder="https://example.com",
            help="Taramaya başlanacak web sitesi URL'ini girin"
        )
        
        # Parameters
        col1, col2 = st.columns(2)
        with col1:
            depth = st.number_input(
                "📊 Derinlik",
                min_value=0,
                max_value=5,
                value=2,
                help="Kaç seviye derinliğe kadar tarama yapılacağını belirler"
            )
        
        with col2:
            limit = st.number_input(
                "📄 Sayfa Limiti",
                min_value=1,
                max_value=100,
                value=10,
                help="Maksimum kaç sayfa taranacağını belirler"
            )
        
        # Start button
        start_crawl = st.button(
            "🚀 Taramayı Başlat",
            type="primary",
            disabled=st.session_state.is_crawling or not url,
            use_container_width=True
        )
        
        st.divider()
        
        # Info
        st.info("""
        **Kullanım Talimatları:**
        1. Taramak istediğiniz web sitesinin URL'ini girin
        2. Derinlik ve sayfa limiti ayarlayın
        3. "Taramayı Başlat" butonuna tıklayın
        4. Sonuçları görüntüleyin ve dışa aktarın
        """)
    
    # Main content area
    if start_crawl and url:
        st.session_state.is_crawling = True
        
        # Create progress containers
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Crawl info
        with st.container():
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.write(f"**Taranan URL:** {url}")
            st.write(f"**Derinlik:** {depth} | **Sayfa Limiti:** {limit}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Execute crawl
        try:
            pipeline = CrawlerPipeline()
            
            # Show live updates
            status_text.text("🔄 Tarama başlatılıyor...")
            progress_bar.progress(10)
            
            # Run the crawler
            with st.spinner("Sayfalar taranıyor..."):
                result = pipeline.crawl(url, max_depth=depth, max_pages=limit)
            
            progress_bar.progress(100)
            status_text.text("✅ Tarama tamamlandı!")
            
            # Store results
            st.session_state.crawl_results = result
            st.session_state.is_crawling = False
            
            # Show success message
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success(f"Tarama başarıyla tamamlandı! Toplam {result.total_crawled} sayfa işlendi.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.session_state.is_crawling = False
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"Tarama sırasında hata oluştu: {str(e)}")
            st.markdown('</div>', unsafe_allow_html=True)
            logger.error(f"Crawl error: {str(e)}")
    
    # Display results
    if st.session_state.crawl_results:
        result = st.session_state.crawl_results
        
        # Metrics
        st.subheader("📊 Tarama İstatistikleri")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Taranan Sayfalar", result.total_crawled)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Toplam Bağlantı", sum(len(p.links) for p in result.pages))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Hata Sayısı", len(result.errors))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Başarı Oranı", f"{(result.total_crawled / (result.total_crawled + len(result.errors)) * 100):.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Results tabs
        st.subheader("📄 Tarama Sonuçları")
        tabs = st.tabs(["📝 İçerik Önizleme", "🔗 Taranan URL'ler", "⚠️ Hatalar", "💾 Dışa Aktarma"])
        
        # Content preview tab
        with tabs[0]:
            if result.pages:
                page_titles = [f"{i+1}. {p.title or p.url}" for i, p in enumerate(result.pages)]
                selected_page_idx = st.selectbox("Sayfa Seçin", range(len(page_titles)), format_func=lambda x: page_titles[x])
                
                if selected_page_idx is not None:
                    page = result.pages[selected_page_idx]
                    
                    # Page info
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**URL:** {page.url}")
                    with col2:
                        st.write(f"**Taranma Zamanı:** {page.crawled_at.strftime('%H:%M:%S')}")
                    
                    # Content
                    if page.cleaned_content:
                        with st.expander("Temizlenmiş İçerik", expanded=True):
                            # Show first 1000 characters
                            content_preview = page.cleaned_content[:1000]
                            if len(page.cleaned_content) > 1000:
                                content_preview += "..."
                            st.text_area("", content_preview, height=300, disabled=True)
                    else:
                        st.warning("Bu sayfa için temizlenmiş içerik bulunamadı.")
            else:
                st.info("Henüz taranmış sayfa bulunmuyor.")
        
        # URLs tab
        with tabs[1]:
            if result.pages:
                st.write(f"**Toplam {len(result.visited_urls)} URL tarandı:**")
                
                # Create a dataframe for better display
                url_data = []
                for page in result.pages:
                    url_data.append({
                        "URL": page.url,
                        "Başlık": page.title or "Başlıksız",
                        "Bağlantı Sayısı": len(page.links),
                        "İçerik Uzunluğu": len(page.cleaned_content) if page.cleaned_content else 0
                    })
                
                st.dataframe(url_data, use_container_width=True)
            else:
                st.info("Henüz taranmış URL bulunmuyor.")
        
        # Errors tab
        with tabs[2]:
            if result.errors:
                st.error(f"Toplam {len(result.errors)} hata oluştu:")
                for error in result.errors:
                    st.write(f"- **{error['url']}**: {error['error']}")
            else:
                st.success("Tarama sırasında hata oluşmadı!")
        
        # Export tab
        with tabs[3]:
            st.write("Tarama sonuçlarını farklı formatlarda dışa aktarabilirsiniz:")
            
            exporter = DataExporter()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📄 JSON İndir", use_container_width=True):
                    json_path = exporter.export_to_json(result)
                    with open(json_path, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="💾 JSON Dosyasını İndir",
                            data=f.read(),
                            file_name=Path(json_path).name,
                            mime="application/json"
                        )
            
            with col2:
                if st.button("📝 Markdown İndir", use_container_width=True):
                    md_path = exporter.export_to_markdown(result)
                    with open(md_path, 'r', encoding='utf-8') as f:
                        st.download_button(
                            label="💾 Markdown Dosyasını İndir",
                            data=f.read(),
                            file_name=Path(md_path).name,
                            mime="text/markdown"
                        )
            
            with col3:
                if st.button("📑 PDF İndir", use_container_width=True):
                    pdf_path = exporter.export_to_pdf(result)
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            label="💾 PDF Dosyasını İndir",
                            data=f.read(),
                            file_name=Path(pdf_path).name,
                            mime="application/pdf"
                        )
            
            st.info("💡 İpucu: Dosyalar aynı zamanda 'data/exports' klasörüne de kaydedilir.")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>AICrawler v1.0 | LangGraph ile geliştirilmiştir | © 2024</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()