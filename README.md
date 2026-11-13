# Garuda Dictionary

**Garuda Prakashan × Rishihood University — Live Project Assignment — Dictionary App Track**

A full-stack Hindi–English dictionary web application that supports search in Devanagari script, Romanised Hindi (with alternate spellings), and English meaning lookup.

> **Disclaimer**: This is a student demonstration project. The dictionary dataset is illustrative and has not been verified by Garuda Prakashan. This application is not an official Garuda Prakashan product.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Features](#3-features)
4. [Technology Stack](#4-technology-stack)
5. [Installation](#5-installation)
6. [Running Locally](#6-running-locally)
7. [Search Algorithm](#7-search-algorithm)
8. [Database Structure](#8-database-structure)
9. [Screenshots](#9-screenshots)
10. [Design Decisions](#10-design-decisions)
11. [Limitations](#11-limitations)
12. [Future Improvements](#12-future-improvements)
13. [Assignment Attribution](#13-assignment-attribution)

---

## 1. Project Overview

Garuda Dictionary is a web application that lets users search for Hindi words in three ways:

- **Devanagari script** — e.g., धर्म, ज्ञान, कर्म
- **Romanised Hindi** — e.g., dharma, gyan, karma (with alternate spellings like dharm, jnana)
- **English meaning** — e.g., knowledge, duty, love

The application includes a live autocomplete search bar, word detail pages, an explore/browse page, and clean JSON API endpoints.

---

## 2. Problem Statement

Hindi speakers and learners encounter friction when searching for dictionary entries online:

- **No standard Romanisation**: the same word can be spelled "dharma", "dharm", or "dharama"
- **Script barrier**: many dictionary apps require Devanagari input exclusively
- **Poor Unicode handling**: diacritical marks and equivalent Unicode representations cause mismatches
- **No alternate-spelling fallback**: a misspelled Romanisation typically returns nothing

Garuda Dictionary addresses all of these by:
- Storing explicit comma-separated alternate Romanisations per entry
- Applying NFC Unicode normalisation before all comparisons
- Supporting multi-tier ranked search from exact to partial to meaning match

---

## 3. Features

### Search
- Exact Devanagari match
- Exact Romanised match (case-insensitive)
- Alternate Romanisation matching (stored per entry)
- Prefix matching (Devanagari and Romanised)
- Partial substring matching
- English meaning / definition search
- Live autocomplete with debounce (280ms)
- Keyboard navigation in autocomplete (Arrow keys, Enter, Escape)
- Works without JavaScript (GET form fallback)

### Pages
- **Homepage**: hero search, word of the day, popular words, how-it-works
- **Search results**: ranked results with definitions and tags
- **Word detail**: full entry, example sentences, etymology, related words, copy/share
- **Explore**: browse all words with letter and part-of-speech filters, pagination
- **About**: project documentation, search algorithm, design decisions

### API
- `GET /api/search/?q=word` — full search results as JSON
- `GET /api/suggestions/?q=word` — lightweight autocomplete suggestions

### Admin
- Full Django Admin interface at `/admin/`
- Search by Devanagari, Romanised, English meaning, definition
- Filter by part of speech, demo status, date

---

## 4. Technology Stack

| Layer | Technology | Reason |
|---|---|---|
| Backend | Python 3, Django | Clean MVC, built-in ORM, admin interface |
| Database | SQLite (via Django ORM) | Zero configuration, portable, sufficient for demo |
| Templates | Django Templates (HTML5) | Server-rendered, works without JavaScript |
| Styling | Custom CSS (CSS custom properties) | Full control, no build tools, beginner-readable |
| JavaScript | Vanilla JS (ES6+) | No dependencies, beginner-readable, browser-native APIs |
| Fonts | Google Fonts (Noto Serif Devanagari, Playfair Display, Inter) | High-quality Unicode, free, CDN-delivered |

---

## 5. Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Setup

```bash
# 1. Clone the repository / enter the project directory
cd garuda_dictionary

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Load the demonstration dataset
python manage.py seed_dictionary

# 6. (Optional) Create an admin superuser
python manage.py createsuperuser
```

---

## 6. Running Locally

```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000/**

Admin interface: **http://127.0.0.1:8000/admin/**

### Running Tests

```bash
python manage.py test dictionary
```

Expected output: `Ran 38 tests in ~0.05s — OK`

### Re-seeding the Database

```bash
# Add entries (skips existing)
python manage.py seed_dictionary

# Clear and re-seed
python manage.py seed_dictionary --clear
```

---

## 7. Search Algorithm

Search operates across six ranked tiers. Results within each tier are sorted alphabetically.

```
Tier 1 — Exact Devanagari match
         e.g., query "धर्म" matches entry with devanagari_word = "धर्म"

Tier 2 — Exact Romanised match (case-insensitive)
         e.g., query "DHARMA" matches romanised_word = "dharma"

Tier 3 — Alternate Romanisation match
         e.g., query "dharm" matches alternate_romanisations = "dharm,dharama"
         (explicitly stored per entry; avoids inaccurate auto-transliteration)

Tier 4 — Prefix match
         e.g., query "dhar" matches romanised_word starting with "dhar"

Tier 5 — Partial substring match
         e.g., query "arma" matches within romanised_word or alternate_romanisations

Tier 6 — English meaning / definition match
         e.g., query "knowledge" matches english_meaning or definition field
```

**Unicode handling**: All queries are NFC-normalised and whitespace-stripped before matching.

**Why not auto-transliteration?** Romanised Hindi has no single accepted standard. Automatic Devanagari→Roman conversion (e.g., ITRANS, ISO 15919) would produce one form but miss common alternate spellings. Storing explicit alternates per entry is more reliable for a dictionary use case.

---

## 8. Database Structure

### Model: `DictionaryEntry`

| Field | Type | Description |
|---|---|---|
| `id` | BigAutoField | Primary key |
| `devanagari_word` | CharField(200) | Word in Devanagari script |
| `romanised_word` | CharField(200) | Primary Romanised transliteration |
| `alternate_romanisations` | CharField(500) | Comma-separated alternate spellings |
| `english_meaning` | CharField(500) | Short English meaning |
| `part_of_speech` | CharField(50) | Grammatical category |
| `definition` | TextField | Full English definition |
| `example_sentence` | CharField(500) | Example in Devanagari |
| `example_translation` | CharField(500) | English translation of example |
| `etymology` | CharField(500) | Word origin notes |
| `source_reference` | CharField(300) | Source or reference note |
| `is_demo_entry` | BooleanField | True = demonstration content only |
| `created_at` | DateTimeField | Creation timestamp |

---

## 9. Screenshots

> *[Add screenshots here after running the application locally]*

Suggested screenshots:
- Homepage with hero search
- Autocomplete dropdown in action
- Search results page
- Word detail page
- Explore/browse page
- Mobile layout

---

## 10. Design Decisions

### Why Django?
Django provides a complete web framework with ORM, admin, template engine, and URL routing in a single package. For a demonstration project that needs to be beginner-readable and self-contained, Django's "batteries-included" philosophy avoids the complexity of wiring together multiple libraries.

### Why SQLite?
SQLite is built into Python's standard library. It requires zero setup, is portable (a single file), and is entirely adequate for a demonstration dataset of ~40–100 entries. For a production deployment with Garuda Prakashan's full dictionary, PostgreSQL would be recommended for full-text search capability.

### Why Vanilla JavaScript?
Keeping JavaScript framework-free means the codebase is accessible to beginners, requires no build tooling, and loads faster. The autocomplete and keyboard navigation are implemented using browser-native APIs — `fetch`, `AbortController`, `navigator.clipboard`, `navigator.share` — all of which are well-supported in modern browsers.

### Why explicit alternate Romanisations?
Automated Romanisation transliteration from Devanagari produces one canonical form (e.g., ISO 15919: "dharm" → "dharma"). But users type "dharm", "dharma", "dharama", and "dhrama" — all of which are common. Storing explicit alternates per entry gives the dictionary editor control over which variants are searchable, without relying on imperfect automatic conversion.

### Design Language
The visual design draws on Indian literary heritage: warm ivory background, deep saffron and terracotta accents, gold borders, and serif typography. The Noto Serif Devanagari font provides excellent Unicode rendering across macOS, Windows, iOS, and Android. The UI avoids the "government website" aesthetic while remaining culturally relevant.

---

## 11. Limitations

- **Small dataset**: ~42 illustrative entries. Not a comprehensive dictionary.
- **No verified content**: Entries are based on common usage and standard references but have not been reviewed by Garuda Prakashan's editorial team.
- **No audio pronunciation**: Audio would require recorded or synthesised files.
- **No user accounts**: No bookmarks, word history, or personalisation.
- **SQLite at scale**: For a full dictionary of thousands of entries, full-text search with PostgreSQL or Elasticsearch would improve performance.
- **No auto-transliteration**: By design — accurate transliteration requires a linguist-verified mapping.

---

## 12. Future Improvements

- Replace demonstration dataset with Garuda Prakashan's authorised, verified dictionary
- Audio pronunciation (recorded or TTS)
- PostgreSQL + full-text search for large datasets
- User bookmarks and reading history
- Synonym / antonym relationships
- Cross-language expansion (Gujarati, Bengali, Tamil, etc.)
- Progressive Web App (PWA) for offline access
- Citation / source tracking for each entry

---

## 13. Assignment Attribution

**Assignment**: Garuda Prakashan × Rishihood University Live Project — Dictionary App Track

**Technology choices** are Django, SQLite, and vanilla JavaScript as specified in the assignment brief.

The current dictionary dataset is illustrative and can be replaced by Garuda Prakashan's authorised, verified dataset. All `is_demo_entry = True` entries are marked as demonstration content and are not presented as official lexicographic content.
