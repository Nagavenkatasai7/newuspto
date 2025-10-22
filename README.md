# USPTO Opposition Trademark Scraper

A comprehensive web application for scraping and analyzing USPTO trademark opposition data. Built with Streamlit, this tool supports single opposition searches, bulk party searches, and batch company validation.

## Features

### 🔍 Single Opposition Search
- Search by opposition number
- Retrieve trademark class data (US and International)
- AI-powered trademark type classification using Claude Vision
- Automatic slogan detection
- Export results in multiple formats (Excel, TSV, copyable format)

### 📦 Bulk Party Search
- Search by company/party name
- Date range filtering for opposition filing dates
- Scrape all oppositions for a specific party
- Three export formats:
  - **Standard Format**: Detailed opposition data with all metadata
  - **Research Format**: Database-ready format with brand_id, gvkey columns
  - **Copyable Format**: Tab-separated format matching single opposition output

### ✅ Batch Company Validation
- Upload Excel file with multiple company names
- Quick validation to check which companies have opposition data
- Export validated results with opposition counts

### 💾 Intelligent Caching
- SQLite database cache for all scraped data
- 30-day TTL for cached records
- Significant cost savings on API calls
- Cache management interface

## Prerequisites

- Python 3.8+
- USPTO API key
- Anthropic Claude API key

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nagavenkatasai7/newuspto.git
   cd newuspto
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   USPTO_API_KEY=your_uspto_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
   
   **Getting API Keys:**
   - **USPTO API Key**: Get from https://tsdrapi.uspto.gov/ts/cd/casestatus/help
   - **Anthropic Claude API Key**: Get from https://console.anthropic.com/

4. **Run the application**
   ```bash
   streamlit run web_app.py
   ```

## Usage

### Single Opposition Search

1. Navigate to the "🔍 Single Opposition Search" tab
2. Enter an opposition number (e.g., "91234567")
3. Click "Fetch Opposition Data"
4. Download results in your preferred format

### Bulk Party Search

1. Navigate to the "📦 Bulk Party Search" tab
2. Enter party name (e.g., "Nike Inc")
3. Set date range (default: 01/01/2012 - 12/31/2022)
4. Click "🔍 Step 1: Find Oppositions"
5. Review the results
6. Click "✅ Confirm & Start Scraping"
7. Wait for scraping to complete
8. Choose export format and download results

**Export Formats:**

- **Standard Format**: Best for analysis and review
  - One row per opposition
  - Comma-separated trademark lists
  - Detailed metadata sheet
  
- **Research Format**: Best for database integration
  - Includes brand_id, gvkey, company name columns
  - Alternating TM Type/Serial Number columns
  - Direct paste into research Excel files
  
- **Copyable Format**: Best for quick Excel paste
  - Tab-separated format
  - Matches single opposition copyable summary
  - Ready for direct paste into Excel

### Batch Company Validation

1. Navigate to the "✅ Batch Company Validation" tab
2. Upload Excel file with company names (Column A)
3. Click "🔍 Validate Companies"
4. Review results showing opposition counts
5. Download validated list

## Export Format Details

### Copyable Format Structure
```
Marks | US GS | INT GS | Opp Start | Opp End | Result | TM Type | Serial | TM Type | Serial | ...
```

### Research Format Structure
```
brand_id | gvkey | conm | Alt Name | Plaintiff | Marks | US GS | INT GS | Opp Start | Opp End | Result | TM Type | Serial | ...
```

**Field Definitions:**
- **Marks**: Number of trademarks in the opposition
- **US GS**: Count of unique US trademark classes
- **INT GS**: Count of unique international trademark classes
- **Opp Start**: Opposition filing date (YYYY-MM-DD)
- **Opp End**: Opposition termination date (YYYY-MM-DD)
- **Result**: 1=Sustained, 0=Dismissed, NA=Pending
- **TM Type**: 0=No Image, 1=Standard Text, 2=Stylized/Design, 3=Slogan
- **Serial**: 8-digit trademark serial number

## Technical Details

### Data Sources
- **USPTO TSDR API**: Trademark status and class data
- **TTABVue**: Opposition metadata and dates
- **Claude Vision API**: AI-powered trademark type classification

### Rate Limiting
- USPTO API: 60 req/min (peak), 120 req/min (off-peak)
- Automatic retry logic with exponential backoff
- Connection error handling

### Caching System
- SQLite database for persistent storage
- 30-day TTL for cached records
- Saves ~$0.015 per cached image classification
- Automatic stale record cleanup

### AI Classification
- **Trademark Type Detection**: Claude Sonnet 4.5 with vision
- **Slogan Detection**: Claude Sonnet 4.5 with text analysis
- Retry logic with fallback mechanisms
- Rate limiting to prevent API overload

## Project Structure

```
├── web_app.py                      # Main Streamlit application
├── database_cache.py               # SQLite caching system
├── research_format_exporter.py    # Research format export functionality
├── bulk_copyable_formatter.py     # Copyable format export functionality
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── RESEARCH_FORMAT_GUIDE.md       # Detailed research format documentation
└── README.md                       # This file
```

## Documentation

- **RESEARCH_FORMAT_GUIDE.md**: Comprehensive guide for Research Format exports
- Includes field definitions, use cases, and examples
- Step-by-step instructions for database integration

## Troubleshooting

### API Errors
- **500 Error (Overloaded)**: Automatic retry with exponential backoff
- **Connection Reset**: Retry logic with increased delays
- Check API key validity in `.env` file

### Empty Results
- Verify party name spelling
- Check date range (oppositions may be outside selected dates)
- Review "Failed Serials" in Standard Format export

### Cache Issues
- Use "Clear Stale" to remove old records
- Use "Clear All" for complete cache reset
- Check database file permissions

## Cost Considerations

- **USPTO API**: Free
- **Claude API**: ~$0.015 per image classification (cached after first run)
- Caching significantly reduces costs for repeated queries

## Contributing

Issues and pull requests welcome at https://github.com/Nagavenkatasai7/newuspto

## License

This project is for research and educational purposes.

## Disclaimer

This tool scrapes publicly available USPTO data. Ensure compliance with USPTO's terms of service and rate limiting guidelines.

---

**Version:** 1.0
**Last Updated:** October 2024
