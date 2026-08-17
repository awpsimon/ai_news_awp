# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI News API is a Python Flask service that automatically generates AI-powered news briefs and flashes in German and French from press releases. It serves AWP (Agence Télégraphique Suisse), the Swiss news agency.

## Commands

```bash
# Run the application
run_ai_news_api.cmd
# Or directly:
venv\Scripts\python.exe main.py

# Run unit tests (text post-processing)
python publisher_tests.py

# Run integration test (full pipeline with sample press release)
python test.py
```

## Architecture

### Request Flow

1. Client POSTs to `/publish` with headline, text, and ISIN
2. Background thread executes `publish_brief()` in `publisher.py`
3. Text is classified via zero-shot classification (`classifier.py`)
4. Company metadata is retrieved from masterdata DB (`company_lookup.py`)
5. AI generates flash and brief for each language using prompts from MySQL
6. `textprocessor.py` post-processes output (number formatting, currency symbols, paragraph structure)
7. Results are saved to MySQL and output as XML files to `_output/`

### Key Components

| File | Purpose |
|------|---------|
| `main.py` | Flask app with `/classify` and `/publish` endpoints |
| `publisher.py` | Core orchestration - generates DE/FR flash/brief, handles DB updates |
| `classifier.py` | Zero-shot text classification using HuggingFace transformers |
| `textprocessor.py` | Swiss German text formatting (e.g., "CHF 1.5 Mio." → "1,5 Millionen Franken") |
| `company_lookup.py` | SQL queries for company metadata (name, ISIN, synonyms, locations) |
| `db_pool.py` | MySQL connection pooling |

### External Dependencies

- **awptools** (internal library): AI prompting via `awptools.prompting`, utilities via `awptools.utils`
- **MySQL databases**: `ai_texts` (prompts, topics, generated content), `masterdata` (company info)
- **Anthropic Claude API**: Used through awptools for text generation

## Text Processing Conventions

The `textprocessor.py` module applies Swiss German formatting rules:
- Converts "CHF" to "Franken" or "Fr." depending on context
- Uses Swiss thousand separator (apostrophe): 1'000'000
- Converts abbreviations: "Mio." → "Millionen", "%" → "Prozent"
- Converts German "ß" to Swiss "ss"
- Inserts paragraph breaks every 2-3 sentences
- Escapes ampersands for XML output

## Database Schema

Prompts and topics are stored in `ai_texts` database:
- Prompts are selected based on classification result and company-specific overrides
- Generation results include flash/brief texts in both languages with metadata

## Output

Generated news items are:
1. Stored in MySQL database
2. Written as XML files to `_output/` directory using awptools utilities
