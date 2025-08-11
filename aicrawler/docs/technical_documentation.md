# AICrawler Teknik Dokümantasyon

## 1. Genel Bakış

AICrawler, LangGraph framework'ü kullanılarak geliştirilmiş, state-based workflow yaklaşımı ile çalışan bir web crawler uygulamasıdır. Uygulama, verilen bir URL'den başlayarak belirtilen derinlik ve limit parametrelerine göre web sayfalarını tarar, HTML içeriğini temizler ve farklı formatlarda export eder.

## 2. Mimari Tasarım

### 2.1 Sistem Mimarisi

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│  LangGraph       │────▶│  Data Storage   │
│   (app.py)      │     │  Workflow        │     │  (JSON/MD/PDF)  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Core Modules       │
                    ├──────────────────────┤
                    │ • Crawler            │
                    │ • Cleaner            │
                    │ • Storage            │
                    └──────────────────────┘
```

### 2.2 LangGraph Workflow

Workflow üç ana node'dan oluşur:

1. **Fetch Node**: Web sayfalarını indirir ve link ekstraksiyonu yapar
2. **Clean Node**: HTML içeriğini temizler ve anlamlı metin çıkarır
3. **Save Node**: İşlenmiş veriyi saklar

```python
workflow = StateGraph(CrawlerState)
workflow.add_node("fetch", fetch_node)
workflow.add_node("clean", clean_node)
workflow.add_node("save", save_node)
```

## 3. Modül Detayları

### 3.1 State Management (state.py)

State yönetimi Pydantic modelleri ile sağlanır:

```python
class CrawlerState(BaseModel):
    start_url: str
    max_depth: int = 2
    max_pages: int = 10
    current_depth: int = 0
    visited_urls: Set[str]
    to_visit: List[tuple[str, int]]
    pages: List[PageContent]
    errors: List[Dict[str, str]]
    status: str = "initialized"
    total_crawled: int = 0
```

### 3.2 Web Crawler (crawler.py)

**Özellikler:**
- Session-based HTTP istekleri
- Otomatik redirect takibi
- Link normalizasyonu
- Derinlik kontrolü
- Rate limiting (0.5s delay)

**Link Ekstraksiyonu:**
- Relative URL'leri absolute'a çevirir
- Fragment'ları temizler
- Duplicate kontrolü yapar
- Sadece HTTP/HTTPS protokollerini kabul eder

### 3.3 HTML Cleaner (cleaner.py)

**Temizleme Stratejisi:**

1. **Tag Temizleme:**
   - Script, style, iframe vb. tagları kaldırır
   - Form elementlerini temizler
   - Multimedia elementlerini siler

2. **İçerik Filtreleme:**
   - Reklam pattern'lerine göre filtreleme
   - Boş tagları kaldırma
   - HTML yorumlarını temizleme

3. **Metin Çıkarma:**
   - Anlamlı paragrafları korur
   - Whitespace normalizasyonu
   - 20 karakterden kısa metinleri filtreler

### 3.4 Storage (storage.py)

**Export Formatları:**

1. **JSON**: Tam veri yapısı, makine okunabilir
2. **Markdown**: İnsan okunabilir, yapılandırılmış
3. **PDF**: Profesyonel rapor formatı

## 4. Streamlit Arayüzü

### 4.1 Kullanıcı Akışı

1. URL ve parametreleri gir
2. Crawl başlat
3. Canlı ilerleme takibi
4. Sonuçları görüntüle
5. Export et

### 4.2 State Management

```python
st.session_state.crawl_results  # Crawl sonuçları
st.session_state.is_crawling    # Crawl durumu
```

## 5. Performans Optimizasyonları

1. **Session Kullanımı**: HTTP bağlantılarını yeniden kullanır
2. **Set Veri Yapısı**: Visited URL kontrolü O(1) karmaşıklığında
3. **Streaming Updates**: Büyük crawl'lar için memory-efficient
4. **Selective Parsing**: Sadece gerekli HTML elementleri parse edilir

## 6. Güvenlik Önlemleri

1. **Timeout Koruması**: 10 saniye HTTP timeout
2. **Depth Limiti**: Sonsuz döngü koruması
3. **Page Limiti**: Kaynak tüketimi kontrolü
4. **Error Handling**: Try-catch blokları ile hata yönetimi

## 7. Konfigürasyon

### 7.1 Ortam Değişkenleri (.env)

```env
DEFAULT_DEPTH=2
DEFAULT_LIMIT=10
EXPORT_DIR=data/exports
USER_AGENT=Mozilla/5.0...
```

### 7.2 Parametre Limitleri

- Max Depth: 5
- Max Pages: 100
- Timeout: 10 saniye
- Delay: 0.5 saniye

## 8. Test Stratejisi

### 8.1 Test Siteleri

1. **quotes.toscrape.com**: Basit HTML yapısı
2. **httpbin.org**: HTTP response testleri
3. **example.com**: Minimal içerik

### 8.2 Test Senaryoları

- Depth=0: Sadece başlangıç sayfası
- Depth>1: Recursive crawling
- 404/500 hataları
- Redirect zinciri
- Büyük sayfalar

## 9. Bilinen Limitasyonlar

1. JavaScript render edilmez (sadece static HTML)
2. robots.txt kontrolü yapılmaz
3. Sitemap desteği yok
4. Authentication desteği yok
5. Proxy desteği yok

## 10. Gelecek Geliştirmeler

1. **Playwright Entegrasyonu**: JavaScript rendering
2. **Async Crawling**: Paralel sayfa işleme
3. **Database Desteği**: SQLite/PostgreSQL
4. **API Endpoint**: REST API servisi
5. **Scheduling**: Periyodik crawl desteği
6. **Custom Extractors**: Sayfa-spesifik veri çıkarma

## 11. API Referansı

### CrawlerPipeline

```python
pipeline = CrawlerPipeline()
result = pipeline.crawl(
    start_url: str,
    max_depth: int = 2,
    max_pages: int = 10
) -> CrawlerState
```

### DataExporter

```python
exporter = DataExporter(export_dir: str = "data/exports")
exporter.export_to_json(state: CrawlerState) -> str
exporter.export_to_markdown(state: CrawlerState) -> str
exporter.export_to_pdf(state: CrawlerState) -> str
```

## 12. Hata Kodları

- `RequestException`: HTTP istek hatası
- `ParseError`: HTML parsing hatası
- `ExportError`: Dosya yazma hatası
- `WorkflowError`: LangGraph akış hatası