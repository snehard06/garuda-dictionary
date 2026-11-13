"""
Tests for Garuda Dictionary.

Covers:
- Exact Devanagari search
- Exact Romanised search (case-insensitive)
- Alternate Romanisation search
- Partial / prefix matching
- English meaning search
- Empty query handling
- Unknown word handling
- Word detail page (HTTP 200)
- API JSON response structure
- Unicode handling (NFC normalisation)
"""

from django.test import TestCase, Client
from django.urls import reverse
import json

from .models import DictionaryEntry


class DictionaryEntrySetupMixin:
    """Creates a minimal set of test entries."""

    @classmethod
    def setUpTestData(cls):
        cls.dharma = DictionaryEntry.objects.create(
            devanagari_word='धर्म',
            romanised_word='dharma',
            alternate_romanisations='dharm,dharama',
            english_meaning='duty, righteousness',
            part_of_speech='noun',
            definition='Dharma is cosmic order and moral law.',
            example_sentence='धर्म की राह पर चलो।',
            example_translation='Walk the path of righteousness.',
            etymology='Sanskrit: धृ (to hold)',
            is_demo_entry=True,
        )
        cls.gyan = DictionaryEntry.objects.create(
            devanagari_word='ज्ञान',
            romanised_word='gyan',
            alternate_romanisations='jnana,gnan',
            english_meaning='knowledge, wisdom',
            part_of_speech='noun',
            definition='Gyan denotes knowledge and wisdom.',
            is_demo_entry=True,
        )
        cls.karma = DictionaryEntry.objects.create(
            devanagari_word='कर्म',
            romanised_word='karma',
            alternate_romanisations='karm',
            english_meaning='action, deed',
            part_of_speech='noun',
            definition='Karma is the universal principle of cause and effect.',
            is_demo_entry=True,
        )


class SearchExactDevanagariTest(DictionaryEntrySetupMixin, TestCase):
    """Test 1: Exact Devanagari search."""

    def test_exact_devanagari_match(self):
        results = DictionaryEntry.search('धर्म')
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].devanagari_word, 'धर्म')

    def test_exact_devanagari_gyan(self):
        results = DictionaryEntry.search('ज्ञान')
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0].devanagari_word, 'ज्ञान')


class SearchExactRomanisedTest(DictionaryEntrySetupMixin, TestCase):
    """Test 2: Exact Romanised search."""

    def test_exact_romanised_lowercase(self):
        results = DictionaryEntry.search('dharma')
        self.assertTrue(any(e.romanised_word == 'dharma' for e in results))

    def test_exact_romanised_karma(self):
        results = DictionaryEntry.search('karma')
        self.assertTrue(any(e.romanised_word == 'karma' for e in results))


class SearchCaseInsensitiveTest(DictionaryEntrySetupMixin, TestCase):
    """Test 3: Case-insensitive Romanised search."""

    def test_uppercase(self):
        results = DictionaryEntry.search('DHARMA')
        self.assertTrue(any(e.romanised_word == 'dharma' for e in results))

    def test_mixed_case(self):
        results = DictionaryEntry.search('Karma')
        self.assertTrue(any(e.romanised_word == 'karma' for e in results))

    def test_all_caps_gyan(self):
        results = DictionaryEntry.search('GYAN')
        self.assertTrue(any(e.romanised_word == 'gyan' for e in results))


class SearchAlternateRomanisationTest(DictionaryEntrySetupMixin, TestCase):
    """Test 4: Alternate Romanisation search."""

    def test_alternate_dharm(self):
        results = DictionaryEntry.search('dharm')
        ids = [e.pk for e in results]
        self.assertIn(self.dharma.pk, ids)

    def test_alternate_jnana(self):
        results = DictionaryEntry.search('jnana')
        ids = [e.pk for e in results]
        self.assertIn(self.gyan.pk, ids)

    def test_alternate_karm(self):
        results = DictionaryEntry.search('karm')
        ids = [e.pk for e in results]
        self.assertIn(self.karma.pk, ids)


class SearchPartialMatchTest(DictionaryEntrySetupMixin, TestCase):
    """Test 5: Partial / prefix matching."""

    def test_prefix_roman(self):
        results = DictionaryEntry.search('dhar')
        ids = [e.pk for e in results]
        self.assertIn(self.dharma.pk, ids)

    def test_partial_in_alternate(self):
        results = DictionaryEntry.search('gnan')
        ids = [e.pk for e in results]
        self.assertIn(self.gyan.pk, ids)


class SearchEnglishMeaningTest(DictionaryEntrySetupMixin, TestCase):
    """Test 6: English meaning search."""

    def test_english_duty(self):
        results = DictionaryEntry.search('duty')
        ids = [e.pk for e in results]
        self.assertIn(self.dharma.pk, ids)

    def test_english_knowledge(self):
        results = DictionaryEntry.search('knowledge')
        ids = [e.pk for e in results]
        self.assertIn(self.gyan.pk, ids)

    def test_english_action(self):
        results = DictionaryEntry.search('action')
        ids = [e.pk for e in results]
        self.assertIn(self.karma.pk, ids)


class SearchEmptyQueryTest(DictionaryEntrySetupMixin, TestCase):
    """Test 7: Empty query handling."""

    def test_empty_string_returns_no_results(self):
        results = DictionaryEntry.search('')
        self.assertEqual(list(results), [])

    def test_whitespace_query_returns_no_results(self):
        results = DictionaryEntry.search('   ')
        self.assertEqual(list(results), [])

    def test_none_via_api(self):
        client = Client()
        response = client.get('/api/search/', {'q': ''})
        self.assertEqual(response.status_code, 400)


class SearchUnknownWordTest(DictionaryEntrySetupMixin, TestCase):
    """Test 8: Unknown word handling."""

    def test_unknown_word_returns_empty(self):
        results = DictionaryEntry.search('xyzunknownword123')
        self.assertEqual(results, [])

    def test_unknown_via_search_view(self):
        client = Client()
        response = client.get(reverse('dictionary:search'), {'q': 'xyzunknownword123'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No results')


class WordDetailPageTest(DictionaryEntrySetupMixin, TestCase):
    """Test 9: Word detail page."""

    def setUp(self):
        self.client = Client()

    def test_word_detail_200(self):
        response = self.client.get(reverse('dictionary:word_detail', args=[self.dharma.pk]))
        self.assertEqual(response.status_code, 200)

    def test_word_detail_contains_devanagari(self):
        response = self.client.get(reverse('dictionary:word_detail', args=[self.dharma.pk]))
        self.assertContains(response, 'धर्म')

    def test_word_detail_contains_meaning(self):
        response = self.client.get(reverse('dictionary:word_detail', args=[self.gyan.pk]))
        self.assertContains(response, 'knowledge')

    def test_word_detail_404_for_missing(self):
        response = self.client.get(reverse('dictionary:word_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)


class ApiSearchTest(DictionaryEntrySetupMixin, TestCase):
    """Test 10: API JSON response."""

    def setUp(self):
        self.client = Client()

    def test_api_search_returns_json(self):
        response = self.client.get('/api/search/', {'q': 'dharma'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        data = json.loads(response.content)
        self.assertIn('results', data)
        self.assertIn('count', data)

    def test_api_search_finds_dharma(self):
        response = self.client.get('/api/search/', {'q': 'dharma'})
        data = json.loads(response.content)
        self.assertGreater(data['count'], 0)
        ids = [r['id'] for r in data['results']]
        self.assertIn(self.dharma.pk, ids)

    def test_api_suggestions_returns_json(self):
        response = self.client.get('/api/suggestions/', {'q': 'dh'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('suggestions', data)

    def test_api_suggestions_empty_query(self):
        response = self.client.get('/api/suggestions/', {'q': ''})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['suggestions'], [])

    def test_api_search_too_long_query(self):
        response = self.client.get('/api/search/', {'q': 'x' * 201})
        self.assertEqual(response.status_code, 400)


class UnicodeHandlingTest(DictionaryEntrySetupMixin, TestCase):
    """Test 11: Unicode and NFC normalisation."""

    def test_nfc_normalisation_does_not_break_search(self):
        import unicodedata
        # Normalise the query the same way the model does
        query = unicodedata.normalize('NFC', 'dharma')
        results = DictionaryEntry.search(query)
        self.assertTrue(any(e.romanised_word == 'dharma' for e in results))

    def test_devanagari_stored_correctly(self):
        entry = DictionaryEntry.objects.get(romanised_word='dharma')
        self.assertEqual(entry.devanagari_word, 'धर्म')

    def test_whitespace_stripped_from_query(self):
        results = DictionaryEntry.search('  gyan  ')
        self.assertTrue(any(e.romanised_word == 'gyan' for e in results))


class HomePageTest(DictionaryEntrySetupMixin, TestCase):
    """Test homepage loads correctly."""

    def test_home_page_200(self):
        response = self.client.get(reverse('dictionary:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_contains_hero_text(self):
        response = self.client.get(reverse('dictionary:home'))
        self.assertContains(response, 'Discover Words')

    def test_home_page_search(self):
        response = self.client.get(reverse('dictionary:home'), {'q': 'karma'})
        self.assertEqual(response.status_code, 200)


class ExplorePageTest(DictionaryEntrySetupMixin, TestCase):
    """Test explore page."""

    def test_explore_page_200(self):
        response = self.client.get(reverse('dictionary:explore'))
        self.assertEqual(response.status_code, 200)

    def test_explore_shows_entries(self):
        response = self.client.get(reverse('dictionary:explore'))
        self.assertContains(response, 'dharma')

    def test_explore_pos_filter(self):
        response = self.client.get(reverse('dictionary:explore'), {'pos': 'noun'})
        self.assertEqual(response.status_code, 200)
