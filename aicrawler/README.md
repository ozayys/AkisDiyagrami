# 🕷️ AICrawler - LangGraph Tabanlı Web İçerik Toplama ve Temizleme Sistemi

AICrawler, LangGraph kullanarak geliştirilmiş akıllı bir web içerik toplama (crawling) ve temizleme aracıdır. Verilen bir başlangıç URL'inden başlayarak, belirtilen derinlik ve sayfa limitlerine göre web sitelerini tarar, HTML içeriğini temizler ve çeşitli formatlarda export eder.

## 🌟 Özellikler

- **LangGraph Workflow**: Adım bazlı iş akışı yönetimi (fetch → clean → save)
- **Çok Katmanlı Tarama**: Derinlik (depth) ve sayfa limiti parametreleri ile kontrollü tarama
- **Akıllı HTML Temizleme**: Script, style, reklam ve gereksiz elementlerin otomatik temizlenmesi
- **Çoklu Export Formatları**: JSON, Markdown ve PDF formatlarında dışa aktarım
- **Modern Web Arayüzü**: Streamlit tabanlı kullanıcı dostu arayüz
- **Canlı İlerleme Takibi**: Tarama sırasında anlık durum güncellemeleri
- **Hata Yönetimi**: Başarısız sayfalar için detaylı hata raporlama

## 📋 Gereksinimler

- Python 3.8+
- Pip paket yöneticisi

## 🚀 Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/yourusername/aicrawler.git
cd aicrawler
```

2. Sanal ortam oluşturun (önerilen):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

## 💻 Kullanım

### Streamlit Web Arayüzü

Streamlit arayüzünü başlatmak için:

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` adresine gidin.

### Komut Satırı Test Script

Test script'ini çalıştırmak için:

```bash
python test_crawler.py
```

### Python API Kullanımı

```python
from src.core.workflow import CrawlerPipeline

# Pipeline oluştur
pipeline = CrawlerPipeline()

# Web sitesini tara
result = pipeline.crawl(
    start_url="https://example.com",
    max_depth=2,
    max_pages=10
)

# Sonuçları kullan
print(f"Taranan sayfa sayısı: {result.total_crawled}")
for page in result.pages:
    print(f"URL: {page.url}")
    print(f"Başlık: {page.title}")
    print(f"İçerik: {page.cleaned_content[:200]}...")
```

## 🏗️ Proje Yapısı

```
aicrawler/
├── app.py                  # Streamlit web arayüzü
├── test_crawler.py         # Test script
├── requirements.txt        # Python bağımlılıkları
├── .env                    # Konfigürasyon dosyası
│
├── src/
│   ├── core/
│   │   ├── state.py       # State tanımlamaları
│   │   ├── crawler.py     # Web crawler modülü
│   │   ├── cleaner.py     # HTML temizleme modülü
│   │   ├── storage.py     # Veri depolama ve export
│   │   └── workflow.py    # LangGraph workflow
│   │
│   ├── utils/             # Yardımcı fonksiyonlar
│   └── ui/                # UI bileşenleri
│
├── data/
│   └── exports/           # Export edilen dosyalar
│
├── docs/                  # Dokümantasyon
└── tests/                 # Test dosyaları
```

## 🔧 Konfigürasyon

`.env` dosyasında ayarlanabilir parametreler:

```env
DEFAULT_DEPTH=2            # Varsayılan tarama derinliği
DEFAULT_LIMIT=10           # Varsayılan sayfa limiti
EXPORT_DIR=data/exports    # Export dizini
USER_AGENT=...             # HTTP User-Agent
```

## 📊 LangGraph Workflow

AICrawler'ın iş akışı 3 ana node'dan oluşur:

1. **Fetch Node**: Web sayfalarını indirir ve linklerini çıkarır
2. **Clean Node**: HTML içeriğini temizler ve anlamlı metni çıkarır
3. **Save Node**: Temizlenmiş veriyi JSON formatında saklar

```
[Start] → [Fetch] → [Should Continue?] → [Clean] → [Save] → [End]
             ↑              ↓
             └──────────────┘
```

## 🧹 HTML Temizleme

Temizlenen elementler:
- Script ve style tagları
- İframe, embed, object elementleri
- Form elementleri
- Reklam içerikleri (class/id pattern matching)
- Boş taglar
- HTML yorumları

## 📤 Export Formatları

### JSON Format
```json
{
  "metadata": {
    "start_url": "https://example.com",
    "max_depth": 2,
    "max_pages": 10,
    "total_crawled": 8,
    "export_date": "2024-01-15T10:30:00"
  },
  "pages": [
    {
      "url": "https://example.com",
      "title": "Example Domain",
      "cleaned_content": "...",
      "metadata": {...}
    }
  ]
}
```

### Markdown Format
- Başlık ve metadata bilgileri
- Her sayfa için ayrı bölüm
- Temizlenmiş içerik önizlemesi
- Hata listesi

### PDF Format
- Profesyonel görünümlü rapor
- Sayfa başlıkları ve içerikleri
- Metadata ve istatistikler

## 🧪 Test

Proje 3 farklı test sitesi ile test edilmiştir:
1. quotes.toscrape.com - Basit yapılı site
2. httpbin.org - HTTP test servisi
3. example.com - Minimal örnek site

## 📝 Notlar

- Crawler, robots.txt kurallarına saygı göstermez (demo amaçlı)
- Her istek arasında 0.5 saniye bekleme süresi vardır
- Büyük siteler için sayfa limitini kullanmanız önerilir

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👥 İletişim

Proje Danışmanı: Yunus Emre DEMİRDAĞ

---

**Not**: Bu proje, LangGraph ile web crawling ve veri temizleme konularında pratik kazanmak amacıyla geliştirilmiş bir staj projesidir.