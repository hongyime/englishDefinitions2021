"""Exercise PDF-to-CSV behavior with synthetic text and no provider requests."""
import contextlib
import csv
import importlib.util
import io
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import patch


class Progress:
    """Minimal context-managed progress sink for offline tests."""

    def __init__(self, **kwargs):
        pass
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def update(self, count):
        """Accept a completed lookup without drawing a progress bar."""


def load_extractor(documents, calls, definitions):
    """Load the real module with PDF and dictionary boundaries replaced."""
    def meaning(word):
        calls.append(word)
        return definitions

    source = Path(__file__).resolve().parents[1] / 'definitions.py'
    extract = SimpleNamespace(extract_text=lambda path: documents[Path(path).name])
    modules = {
        'pdfminer': SimpleNamespace(high_level=extract),
        'pdfminer.high_level': extract,
        'PyDictionary': SimpleNamespace(PyDictionary=lambda: SimpleNamespace(meaning=meaning)),
        'tqdm': SimpleNamespace(tqdm=Progress),
    }
    spec = importlib.util.spec_from_file_location('definitions_under_test', source)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class DefinitionsTests(TestCase):
    """Check observable PDF-to-CSV behavior using only synthetic records."""

    def run_extraction(self, text, definitions=None):
        """Run in a temporary directory and return calls, CSV rows and header."""
        calls = []
        original = Path.cwd()
        with TemporaryDirectory() as directory:
            texts = text if isinstance(text, list) else ([] if text is None else [text])
            documents = {f'synthetic-{index}.pdf': content for index, content in enumerate(texts)}
            for filename in documents:
                (Path(directory) / filename).touch()
            try:
                os.chdir(directory)
                with contextlib.redirect_stdout(io.StringIO()):
                    module = load_extractor(documents, calls, definitions)
                    self.assertFalse(Path('definitions_of_words.csv').exists())
                    self.assertEqual(calls, [])
                    module.get_definitions_of_words_from_pdf()
                with open('definitions_of_words.csv', newline='', encoding='utf-8') as output:
                    reader = csv.DictReader(output)
                    return calls, list(reader), reader.fieldnames
            finally:
                os.chdir(original)

    def test_common_words_never_trigger_dictionary_requests(self):
        """Exclude common vocabulary before requesting a definition."""
        calls, rows, _ = self.run_extraction(
            'about after nebulous', {'Noun': ['synthetic meaning']})
        self.assertEqual(calls, ['nebulous'])
        self.assertEqual([row['word'] for row in rows], ['NEBULOUS'])

    def test_repeated_words_keep_their_frequency_with_one_lookup(self):
        """Count occurrences instead of counting deduplicated words."""
        calls, rows, _ = self.run_extraction(
            'nebulous nebulous nebulous', {'Adjective': ['synthetic meaning']})
        self.assertEqual(calls, ['nebulous'])
        self.assertEqual([(row['word'], row['frequency']) for row in rows], [('NEBULOUS', '3')])

    def test_empty_input_and_missing_definitions_still_export_a_header(self):
        """Produce valid empty CSV output for either empty-result path."""
        for text in [None, 'nebulous']:
            with self.subTest(text=text):
                _, rows, header = self.run_extraction(text)
                self.assertEqual(rows, [])
                self.assertEqual(header, ['frequency', 'word', 'definitions'])

    def test_multiple_parts_of_speech_keep_the_same_frequency(self):
        """Retain every supported part of speech with its occurrence count."""
        _, rows, _ = self.run_extraction(
            'nebulous nebulous', {'Noun': ['first'], 'Verb': ['second']})
        self.assertEqual(len(rows), 2)
        self.assertEqual([row['frequency'] for row in rows], ['2', '2'])

    def test_whitespace_punctuation_case_and_edge_letters_are_preserved(self):
        """Split PDF whitespace and keep real n characters at word edges."""
        calls, rows, _ = self.run_extraction(
            'Nebulous\nnebulous\tcanyon; canyon', {'Noun': ['meaning']})
        self.assertEqual(calls, ['canyon', 'nebulous'])
        self.assertEqual(
            [(row['word'], row['frequency']) for row in rows],
            [('CANYON', '2'), ('NEBULOUS', '2')])

    def test_frequency_is_combined_across_documents(self):
        """Count the same normalized word across PDF files."""
        calls, rows, _ = self.run_extraction(['Nebulous', 'nebulous'], {'Adjective': ['meaning']})
        self.assertEqual(calls, ['nebulous'])
        self.assertEqual(rows[0]['frequency'], '2')

    def test_existing_length_and_alphabetic_filters_remain(self):
        """Preserve length and alphabetic restrictions while excluding common words."""
        calls, rows, _ = self.run_extraction(
            'abcd abcdefghijklmno abc12 about', {'Noun': ['meaning']})
        self.assertEqual(calls, [])
        self.assertEqual(rows, [])


if __name__ == '__main__':
    main()
