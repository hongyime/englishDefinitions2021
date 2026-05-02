# PRD: englishDefinitions2021

## Overview
A Python script that reads all PDF files in the current directory, extracts uncommon English words (filtering out ~600 common words), looks up their definitions via PyDictionary, counts word frequency, and writes results to a CSV. Built for academic vocabulary enrichment — e.g., processing a textbook PDF to find words worth studying.

## Goals
- Parse all PDFs in the working directory using pdfminer
- Filter out common English words (stop-word list of ~600 words)
- Look up definitions (noun, adjective, verb, adverb) for remaining words
- Count word frequency across all PDFs
- Export results to `definitions_of_words.csv`

## Non-Goals
- GUI interface
- Support for non-PDF document formats
- Handling non-English text
- Caching API results between runs
- Semantic deduplication (same concept, different word forms)

## User Stories
- As a student, I have a PDF textbook and want to identify unfamiliar words with their definitions automatically.
- As a researcher, I want to find the most frequently used uncommon words across a set of academic papers.
- As a language learner, I want a CSV I can import into Anki for flashcard study.

## Tech Stack
- **Language**: Python 3.x
- **Libraries**: `pdfminer.six`, `PyDictionary`, `tqdm`, `csv` (stdlib), `collections.Counter` (stdlib), `pathlib` (stdlib)

## Architecture
```
englishDefinitions2021/
├── definitions.py          # main script
└── definitions_of_words.csv  # output (generated)
```

Single function `get_definitions_of_words_from_pdf()`:
1. Discover all `.pdf` files in current directory
2. Extract raw text via `pdfminer.high_level.extract_text()`
3. Tokenize by spaces, strip punctuation
4. Filter: keep words with 5–14 chars, alpha-only, not in common-words list
5. Build frequency `Counter`
6. For each unique uncommon word, call `PyDictionary.meaning()`
7. Collect noun/verb/adjective/adverb definitions
8. Sort by custom quicksort (alphabetical)
9. Write to CSV (only words with frequency < 2)

## Features (detailed)

### PDF Text Extraction
- Uses `pdfminer.high_level.extract_text()` on each `.pdf` in working dir
- Strips: `!@#$%'"©^&*().\\|/{}[]<>●,-+=_~`` and whitespace escapes
- **Acceptance**: text is readable ASCII-ish strings from each page

### Word Filtering
- Min length: 5 chars, max: 14 chars
- Must be alphabetic (`str.isalpha()`)
- Must not appear in the hardcoded ~600-word common-words list
- **Acceptance**: words like "the", "have", "information" are excluded

### Definition Lookup
- Uses `PyDictionary` (wraps WordNet / web API)
- Stores up to 4 definition types per word: Noun, Adjective, Verb, Adverb
- Skips words with no definitions found (`None` return)
- **Acceptance**: word "ephemeral" returns at least one definition type

### Custom Sort
- Implements quicksort (recursive, pivot = last element)
- Sorts alphabetically before CSV export
- **Acceptance**: output CSV is alphabetically ordered

### CSV Export
- Columns: `frequency`, `word` (uppercase), `definitions` (list)
- Filters out words with frequency ≥ 2 (only rare words exported)
- **Acceptance**: CSV opens correctly in Excel/Sheets

## Data / Config
| Item | Description |
|------|-------------|
| Input | All `.pdf` files in the same directory as `definitions.py` |
| Output | `definitions_of_words.csv` in same directory |
| Filter threshold | Words with frequency < 2 only (line 1217) |
| Length range | 5–14 characters (line 1134) |

These thresholds are hardcoded constants — modify in-place to adjust behavior.

## Deployment / Run
```bash
pip install pdfminer.six PyDictionary tqdm
# Place PDF files in the same directory
python definitions.py
```

## Constraints & Notes
- **Speed**: PyDictionary makes web requests; large PDFs with many unique words can take minutes
- **Common-words list**: ~600 words hardcoded — not a comprehensive NLP stopword list
- **Frequency filter**: exports only words appearing once (rare words); increase threshold for common ones
- **Quicksort**: custom implementation (not stdlib sorted) — O(n²) worst case but fine for thousands of words
- **Encoding**: output CSV is UTF-8
