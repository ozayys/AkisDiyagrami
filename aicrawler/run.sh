#!/bin/bash

# AICrawler Run Script

echo "🕷️ AICrawler - Web İçerik Toplama ve Temizleme Sistemi"
echo "=================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Sanal ortam bulunamadı. Oluşturuluyor..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Sanal ortam aktifleştiriliyor..."
source venv/bin/activate 2>/dev/null || venv\Scripts\activate

# Install requirements if needed
echo "📚 Bağımlılıklar kontrol ediliyor..."
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p data/exports

echo ""
echo "✅ Kurulum tamamlandı!"
echo ""
echo "Seçenekler:"
echo "1) Streamlit Web Arayüzünü Başlat"
echo "2) Test Script'ini Çalıştır"
echo "3) Python Shell'i Aç"
echo "4) Çıkış"
echo ""

read -p "Seçiminiz (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Streamlit arayüzü başlatılıyor..."
        echo "Tarayıcınızda http://localhost:8501 adresine gidin"
        echo ""
        streamlit run app.py
        ;;
    2)
        echo ""
        echo "🧪 Test script'i çalıştırılıyor..."
        echo ""
        python test_crawler.py
        ;;
    3)
        echo ""
        echo "🐍 Python shell açılıyor..."
        echo "Örnek kullanım:"
        echo ">>> from src.core.workflow import CrawlerPipeline"
        echo ">>> pipeline = CrawlerPipeline()"
        echo ">>> result = pipeline.crawl('https://example.com', max_depth=2, max_pages=10)"
        echo ""
        python
        ;;
    4)
        echo "👋 Güle güle!"
        exit 0
        ;;
    *)
        echo "❌ Geçersiz seçim!"
        exit 1
        ;;
esac