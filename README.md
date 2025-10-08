# Multi-Source Nepali News Summarizer

A comprehensive Python pipeline that scrapes the latest articles from multiple Nepali news sources, extracts clean Nepali text, and generates intelligent summaries using LLM APIs. The tool supports **Nepali Paisa**, **Bikash News**, and **Mero Lagani** with specialized content extraction for each source.

## Features

- 🌐 **Multi-Source Scraping**: Extracts articles from 3 major Nepali news sources
  - **Nepali Paisa** (nepalipaisa.com)
  - **Bikash News** (bikashnews.com) 
  - **Mero Lagani** (merolagani.com)
- 🎯 **Intelligent Content Extraction**: Source-specific parsing with browser fallback
- 🧹 **Advanced Content Cleaning**: Removes sidebar content, PDF controls, and navigation elements
- 🇳🇵 **Nepali Text Processing**: Handles Devanagari script and Unicode normalization
- 🤖 **AI Summarization**: Uses DeepSeek or similar LLM APIs for intelligent summarization
- 📊 **Quality Reports**: Generates human-readable reports for verification
- 🔄 **Retry Logic**: Robust error handling with automatic retries
- 📝 **Comprehensive Logging**: Detailed logging with loguru and screenshot debugging

## Tech Stack
- **Python**: 3.10+
- **Web Scraping**: requests, beautifulsoup4, playwright (for JavaScript rendering)
- **Browser Automation**: Playwright (headless Chrome/Firefox)
- **Environment**: python-dotenv
- **Logging**: loguru
- **Testing**: pytest
## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

1. **Clone or download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd nepali-news-summarizer
   
   # Or download and extract the ZIP file
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers (REQUIRED for JavaScript content)**
   ```bash
   # This downloads browser binaries (Chrome, Firefox, Safari)
   # One-time setup, ~300MB download
   playwright install
   
   # Or install only Chromium (smaller download)
   playwright install chromium
   ```

### 5. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required: DEEPSEEK_API_KEY
# Optional: Google Drive upload (see RCLONE_SETUP.md)
```

### 6. Verify Installation
```bash
# Run tests
pytest --maxfail=1 -q

# Check Python imports
python -c "import requests, bs4, playwright; print('✅ All dependencies imported successfully')"

# Test content extraction
python -m src.content_extractor https://www.nepalipaisa.com/news-detail/87090

# Quick test of scraper (Step 2 feature)
python -c "from src.scraper_links import get_latest_article_links; print(get_latest_article_links())"
```

## Project Structure

```
multi-source-nepali-news/
├── README.md                    # This file
├── main.py                     # Main pipeline script - run this!
├── requirements.txt            # Python dependencies
├── install_deps.sh            # Setup helper script
├── .env                       # Your API keys (create from .env.example)
├── .env.example               # Environment template with Google Drive config
├── src/                       # Source code
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration and settings
│   ├── scraper_links.py      # Multi-source link scraping
│   ├── content_extractor.py  # Advanced content extraction with source-specific cleaning
│   ├── article_summarizer.py # LLM-powered summarization
│   ├── llm_api.py           # LLM API client (DeepSeek, etc.)
│   ├── google_drive_uploader.py # Legacy Google Drive API uploader (deprecated)
│   ├── rclone_uploader.py # Rclone-based Google Drive uploader (recommended)
│   └── utils.py             # HTTP utilities and helpers
├── logs/                      # Log files and debugging
│   └── screenshots/          # Browser screenshots for debugging
├── tests/                     # Test files
│   └── test_*.py            # Comprehensive test suite
├── venv/                      # Virtual environment (created during setup)
├── multi_source_links.json   # Output: Article URLs from all sources
├── multi_source_articles.json # Output: Clean extracted content
└── multi_source_summaries.json # Output: AI-generated summaries
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DEEPSEEK_API_KEY` | DeepSeek API key for summarization | Yes |
| `DEEPSEEK_API_URL` | DeepSeek API endpoint | No (has default) |
| `USER_AGENT` | Browser user agent for scraping | No (has default) |
| `REQUEST_TIMEOUT` | HTTP request timeout in seconds | No (default: 30) |
| `MAX_RETRIES` | Maximum retry attempts | No (default: 3) |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No (default: INFO) |
| `DEBUG` | Enable debug mode | No (default: False) |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Path to Google service account JSON | No (legacy) |
| `UPLOAD_TO_GOOGLE_DRIVE` | Enable Google Drive upload | No (default: False) |
| `RCLONE_CONFIG_NAME` | Rclone remote configuration name | No (default: nepali-news) |

## Development Notes

- **No Docker**: This project runs locally without containerization
- **Logging**: Uses loguru for structured, colored logging
- **Error Handling**: Implements tenacity for robust retry logic
- **Testing**: pytest framework ready for unit and integration tests
- **Code Style**: Follow PEP 8 standards

## API Keys Setup

1. **DeepSeek API**: Sign up at [DeepSeek Platform](https://platform.deepseek.com/)
   - Get your API key from the dashboard
   - Add to `.env` as `DEEPSEEK_API_KEY=your_key_here`

2. **Alternative APIs**: The project supports other LLM providers
   - Uncomment relevant API key variables in `.env`
   - Modify the LLM client in future implementation steps

3. **Google Drive Integration**: Automatically upload posts to Google Drive
   - Uses **Rclone** for reliable automation (GitHub Actions compatible)
   - See [RCLONE_SETUP.md](RCLONE_SETUP.md) for detailed setup
   - Creates organized folder structure: `Nepali News Posts/YYYY-MM-DD/morning|afternoon|evening/`

## Troubleshooting

### Common Issues

1. **Python Version**: Ensure Python 3.10+ is installed
   ```bash
   python --version
   ```

2. **Virtual Environment**: Always activate before running
   ```bash
   # Windows
   venv\Scripts\activate
   # macOS/Linux  
   source venv/bin/activate
   ```

3. **Missing API Keys**: Check `.env` file exists and contains valid keys
   ```bash
   cat .env | grep DEEPSEEK_API_KEY
   ```

4. **Import Errors**: Reinstall dependencies
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## Usage

### Run the Complete Pipeline
```bash
# Run the full multi-source pipeline
python main.py
```

This will execute the complete workflow:

1. **Multi-Source Scraping**: Scrape latest articles from all 3 sources
   - Nepali Paisa: 2 latest articles
   - Bikash News: 2 latest articles  
   - Mero Lagani: 2 latest articles

2. **Intelligent Content Extraction**: Extract clean content using:
   - **Browser fallback** for JavaScript-heavy sites
   - **Source-specific cleaning** for each news source
   - **Sidebar removal** and navigation filtering
   - **PDF control removal** (for Bikash News)

3. **AI Summarization**: Generate concise summaries using LLM APIs

4. **Output Generation**: Save results to structured JSON files:
   - `multi_source_links.json` - Article URLs and metadata from all sources
   - `multi_source_articles.json` - Clean extracted Nepali content
   - `multi_source_summaries.json` - AI-generated summaries

### Test Individual Components

```bash
# Test content extraction for specific sources
python -m src.content_extractor https://www.nepalipaisa.com/news-detail/87090
python -m src.content_extractor https://www.bikashnews.com/story/557537/
python -m src.content_extractor https://merolagani.com/NewsDetail.aspx?newsID=119026

# Test link scraping
python -c "from src.scraper_links import get_multi_source_articles; print(get_multi_source_articles(['nepalipaisa', 'bikashnews', 'merolagani']))"
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Test scraper component
pytest tests/test_scraper_links.py -v

# Run with coverage (if pytest-cov is installed)
pytest tests/ --cov=src
```

### Testing Strategy
The project uses a **live testing** approach:
- `pytest` framework for unit tests of all modules
- **Live integration testing**: `python main.py` tests the complete multi-source pipeline
- **CLI testing**: `python -m src.content_extractor <url>` for content extraction verification
- Real network calls provide authentic testing of Nepali content extraction from all sources

## Content Extraction Features

### Source-Specific Optimizations

#### Nepali Paisa (nepalipaisa.com)
- ✅ **Browser fallback**: Uses Playwright for JavaScript rendering
- ✅ **Content cleaning**: Removes navigation and promotional content
- ✅ **Dateline removal**: Filters out location prefixes (काठमाडौं :, etc.)

#### Bikash News (bikashnews.com)
- ✅ **Browser fallback**: Uses Playwright for JavaScript rendering
- ✅ **Advanced content cleaning**: Removes PDF viewer controls, sidebar content
- ✅ **Sidebar filtering**: Excludes "Share News लोकप्रिय", related news headlines
- ✅ **Duplicate content removal**: Filters out repeated titles and metadata

#### Mero Lagani (merolagani.com)
- ✅ **Browser fallback**: Uses Playwright for JavaScript rendering
- ✅ **Sidebar exclusion**: Removes stock market related sidebar content
- ✅ **Content filtering**: Excludes investment-related navigation elements

### Technical Improvements

- 🎯 **Intelligent parser selection**: Automatically chooses browser fallback for JavaScript-heavy sites
- 🧹 **Multi-layer content cleaning**: Source-specific + generic cleaning patterns
- 🔍 **Nepali text detection**: Validates substantial Devanagari content
- 📸 **Debug screenshots**: Saves browser screenshots for troubleshooting
- 🔄 **Robust error handling**: Graceful fallbacks and comprehensive logging

## Architecture

### Content Extraction Pipeline

```
URL Input → Domain Detection → Parser Selection → Content Extraction → Source-Specific Cleaning → Output
     ↓              ↓                ↓                    ↓                      ↓              ↓
  Article URL   JS-Heavy?     Browser/Standard     Raw HTML Content      Clean Article    JSON Output
                   ↓              ↓                    ↓                      ↓
              bikashnews.com   Playwright         BeautifulSoup        Bikash-specific
              nepalipaisa.com   Rendering         HTML Parsing         cleaning rules
              merolagani.com
```

## Development Status

This is a **complete multi-source Nepali news pipeline**. All major components implemented:

- ✅ **Multi-source scraping**: Nepali Paisa, Bikash News, Mero Lagani
- ✅ **Intelligent content extraction**: Browser fallback with source-specific cleaning
- ✅ **Advanced content filtering**: Removes sidebar, PDF controls, navigation
- ✅ **AI summarization**: LLM-powered summary generation
- ✅ **Comprehensive logging**: Detailed logs with screenshot debugging
- ✅ **Quality assurance**: Human-readable reports and validation

### Recent Improvements
- 🔧 **Fixed Bikash News content extraction**: Added specialized cleaning for PDF controls and sidebar content
- 🎯 **Enhanced content filtering**: Source-specific patterns for cleaner article extraction
- 📊 **Improved output quality**: Better content validation and error handling

## Social Media Post Generation

Generate beautiful social media posts with multiple summaries per image using the collected news summaries.

### Setup for Post Generation

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Install Playwright browsers** (one-time setup):
   ```bash
   playwright install chromium
   ```
3. **Ensure background image**: Place `background.png` in project root

### Generate Posts (Recommended - Perfect Nepali Rendering)

```bash
# Using Playwright (browser-based rendering - handles complex Devanagari perfectly)
python -m src.generate_posts_playwright --force

# Generate multiple posts if summaries don't fit in one
python -m src.generate_posts_playwright --force --max-per-post 8

# Output: output/combined_news_post_*.png (multiple files if needed)
```

**Why Playwright?** It uses browser rendering which perfectly handles complex Nepali conjunct characters (क्ष, ग्र, स्त, र्ग) that PIL cannot render properly.

**Features:**
- ✅ Perfect Devanagari text rendering with all conjuncts
- ✅ Automatic multi-post generation if content doesn't fit
- ✅ Continuous numbering across multiple posts
- ✅ Same background for all posts (consistent branding)
- ✅ 9:16 aspect ratio (1080x1920) perfect for Instagram/Facebook Stories

### Alternative Method (PIL-based - may have text rendering issues)

```bash
# Using PIL/Pillow (faster but may not render complex Nepali text correctly)
python -m src.generate_multi_summary_posts --force
```

Posts are saved in `output/` directory.

## 🤖 Automated GitHub Actions

This project includes automated workflows that run 3 times daily to scrape news and generate posts.

### Schedule (Nepal Time)

| Time | News Range | Description |
|------|------------|-------------|
| 10:30 AM | 5:30 AM - 10:30 AM | Morning news |
| 3:30 PM | 11:00 AM - 3:30 PM | Afternoon news |
| 8:30 PM | 3:30 PM - 8:30 PM | Evening news |

### Setup GitHub Actions

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Add API Key Secret**:
   - Go to Settings → Secrets and variables → Actions
   - Add secret: `DEEPSEEK_API_KEY` with your OpenRouter API key

3. **Enable Actions**: Go to Actions tab and enable workflows

See [GITHUB_SETUP.md](GITHUB_SETUP.md) for detailed instructions.

### Features

- ✅ **Fully automated**: No manual intervention required
- ✅ **No article limits**: Scrapes all available news from each source
- ✅ **Multi-post support**: Automatically creates multiple posts if needed
- ✅ **Archived results**: All posts saved to `archives/` directory
- ✅ **Downloadable artifacts**: Access posts from GitHub Actions artifacts

