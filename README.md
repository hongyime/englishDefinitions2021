# English Definitions Extractor

Project documentation: https://hongyime.github.io/englishDefinitions2021/

The extractor runs locally with Python; GitHub Pages does not run the PDF processing or dictionary lookups.

![Project screenshot](./screenshot.png)


A Python tool to extract uncommon English words from PDF files and retrieve their definitions.

## Description

This project extracts text from PDF documents, identifies uncommon words by filtering out common vocabulary, and retrieves their definitions using an online dictionary API. The results are exported to a CSV file with word frequency counts, making it useful for building vocabulary lists or studying new words from academic papers, books, or other PDF documents.

## Features

- Extract text from PDF files in the current directory
- Filter out common English words using a comprehensive word list
- Look up definitions for nouns, verbs, adjectives, and adverbs
- Track word frequency across documents
- Export results to CSV format with definitions

## Technologies Used

- Python
- pdfminer (PDF text extraction)
- PyDictionary (dictionary API wrapper)
- tqdm (progress bar display)

## Installation

```bash
# Clone the repository
git clone https://github.com/hongyime/englishDefinitions2021.git

# Navigate to project directory
cd englishDefinitions2021

# Install dependencies
pip install pdfminer.six PyDictionary tqdm
```

## Usage

```bash
# Place your PDF files in the project directory
# Run the script
python definitions.py
```

The script will:
1. Scan the current directory for PDF files
2. Extract and process text from each PDF
3. Look up definitions for uncommon words
4. Generate a `definitions_of_words.csv` file with the results

Words are matched without regard to case and counted across all PDFs. Whitespace
and punctuation separate words; the existing 5–14 letter limit and common-word
list apply before lookups. Each unique uncommon word gets one lookup per run.
Repeated words remain in the CSV with their full frequency, with one row for each
available supported part of speech. If no words have definitions, the CSV still
contains its header. Running the script replaces that generated CSV; importing
the module does not run extraction.

PDF processing and the generated CSV are local. The dictionary provider receives
the words being looked up. Its availability and response format are external
dependencies; the regression checks below do not verify the live provider.

## Regression checks

```bash
python -B -m unittest discover -s tests -v
```

The tests use synthetic PDF text, a fake dictionary and temporary output files.
They check filtering, spelling, case, counts across documents, empty results and
CSV output without installing application dependencies or making network requests.

## Demo

See `sampledefinitions.csv` for an example of the output format.

## Disclaimer

1. FOR EDUCATIONAL PURPOSES ONLY
2. USE AT YOUR OWN DISCRETION

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
