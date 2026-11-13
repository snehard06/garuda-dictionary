"""
DictionaryEntry model for Garuda Dictionary.

This model stores Hindi dictionary entries with Devanagari script,
Romanised spellings, English meanings, and linguistic metadata.
"""

import unicodedata
from django.db import models
from django.utils import timezone


class DictionaryEntry(models.Model):
    """
    Represents a single dictionary entry.

    Supports searching by Devanagari script, Romanised Hindi, and English meaning.
    """

    # ── Core word fields ──────────────────────────────────────────────────────
    devanagari_word = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Word in Devanagari script, e.g. धर्म"
    )
    romanised_word = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Primary Romanised transliteration, e.g. dharma"
    )
    alternate_romanisations = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text="Comma-separated alternate spellings, e.g. dharm,dharma"
    )
    english_meaning = models.CharField(
        max_length=500,
        help_text="Short English meaning, e.g. duty, righteousness"
    )

    # ── Linguistic metadata ───────────────────────────────────────────────────
    PART_OF_SPEECH_CHOICES = [
        ('noun', 'Noun (संज्ञा)'),
        ('verb', 'Verb (क्रिया)'),
        ('adjective', 'Adjective (विशेषण)'),
        ('adverb', 'Adverb (क्रियाविशेषण)'),
        ('pronoun', 'Pronoun (सर्वनाम)'),
        ('preposition', 'Postposition (परसर्ग)'),
        ('conjunction', 'Conjunction (समुच्चयबोधक)'),
        ('interjection', 'Interjection (विस्मयादिबोधक)'),
        ('other', 'Other'),
    ]
    part_of_speech = models.CharField(
        max_length=50,
        choices=PART_OF_SPEECH_CHOICES,
        default='noun'
    )
    definition = models.TextField(
        help_text="Detailed definition in English"
    )
    example_sentence = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text="Example sentence in Hindi (Devanagari)"
    )
    example_translation = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text="English translation of the example sentence"
    )
    etymology = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text="Word origin / etymology note"
    )
    source_reference = models.CharField(
        max_length=300,
        blank=True,
        default='',
        help_text="Source reference or note (e.g. Sanskrit root)"
    )

    # ── Admin / metadata ──────────────────────────────────────────────────────
    is_demo_entry = models.BooleanField(
        default=True,
        help_text="True for demonstration entries not verified by Garuda Prakashan"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Dictionary Entry"
        verbose_name_plural = "Dictionary Entries"
        ordering = ['devanagari_word']

    def __str__(self):
        return f"{self.devanagari_word} ({self.romanised_word})"

    def get_alternate_romanisations_list(self):
        """Return alternate romanisations as a Python list."""
        if not self.alternate_romanisations:
            return []
        return [s.strip() for s in self.alternate_romanisations.split(',') if s.strip()]

    @classmethod
    def search(cls, query):
        """
        Multi-tier search returning a ranked QuerySet.

        Priority:
          1. Exact Devanagari match
          2. Exact Romanised match (case-insensitive)
          3. Alternate Romanisation match
          4. Prefix match (Devanagari or Romanised)
          5. Partial match
          6. English meaning match
        """
        if not query:
            return cls.objects.none()

        # Normalise Unicode (NFC) and strip whitespace
        query = unicodedata.normalize('NFC', query.strip())

        # Return empty if query is blank after stripping
        if not query:
            return []

        results = []
        seen_ids = set()

        def add_entries(qs, rank):
            for entry in qs:
                if entry.pk not in seen_ids:
                    seen_ids.add(entry.pk)
                    results.append((rank, entry))

        # 1. Exact Devanagari match
        add_entries(cls.objects.filter(devanagari_word=query), 1)

        # 2. Exact Romanised match (case-insensitive)
        add_entries(cls.objects.filter(romanised_word__iexact=query), 2)

        # 3. Alternate Romanisation match (stored as comma-separated string)
        #    We use icontains on the field; false positives are acceptable for small datasets.
        for entry in cls.objects.exclude(alternate_romanisations=''):
            if entry.pk not in seen_ids:
                alts = entry.get_alternate_romanisations_list()
                if any(alt.lower() == query.lower() for alt in alts):
                    seen_ids.add(entry.pk)
                    results.append((3, entry))

        # 4. Prefix match – Devanagari
        add_entries(cls.objects.filter(devanagari_word__startswith=query), 4)

        # 4b. Prefix match – Romanised
        add_entries(cls.objects.filter(romanised_word__istartswith=query), 4)

        # 5. Partial match – Devanagari
        add_entries(cls.objects.filter(devanagari_word__icontains=query), 5)

        # 5b. Partial match – Romanised
        add_entries(cls.objects.filter(romanised_word__icontains=query), 5)

        # 5c. Alternate romanisation partial
        add_entries(cls.objects.filter(alternate_romanisations__icontains=query), 5)

        # 6. English meaning match
        add_entries(cls.objects.filter(english_meaning__icontains=query), 6)

        # 6b. Definition partial match
        add_entries(cls.objects.filter(definition__icontains=query), 6)

        # Sort by rank then alphabetically
        results.sort(key=lambda x: (x[0], x[1].romanised_word.lower()))
        return [entry for _rank, entry in results]

    @classmethod
    def get_suggestions(cls, query, limit=8):
        """
        Return lightweight suggestion dicts for autocomplete.
        """
        if not query or len(query.strip()) < 1:
            return []

        query = unicodedata.normalize('NFC', query.strip())

        suggestions = []
        seen_ids = set()

        def add(qs):
            for e in qs[:limit]:
                if e.pk not in seen_ids and len(suggestions) < limit:
                    seen_ids.add(e.pk)
                    suggestions.append({
                        'id': e.pk,
                        'devanagari': e.devanagari_word,
                        'romanised': e.romanised_word,
                        'meaning': e.english_meaning,
                    })

        add(cls.objects.filter(devanagari_word__startswith=query))
        add(cls.objects.filter(romanised_word__istartswith=query))
        add(cls.objects.filter(romanised_word__icontains=query))
        add(cls.objects.filter(alternate_romanisations__icontains=query))
        add(cls.objects.filter(english_meaning__icontains=query))

        return suggestions[:limit]

    @classmethod
    def get_word_of_day(cls):
        """Return a word of the day based on today's date (deterministic)."""
        from datetime import date
        today = date.today()
        total = cls.objects.count()
        if total == 0:
            return None
        # Use day-of-year as a consistent index
        idx = today.timetuple().tm_yday % total
        return cls.objects.all()[idx]

    @classmethod
    def get_popular_words(cls, limit=12):
        """Return a curated selection of popular/featured words."""
        featured = ['dharma', 'karma', 'yoga', 'gyan', 'satya', 'ahimsa',
                    'sanskriti', 'shiksha', 'pustak', 'vichar', 'anand', 'shakti']
        result = []
        for word in featured:
            qs = cls.objects.filter(romanised_word__iexact=word)
            if qs.exists():
                result.append(qs.first())
            if len(result) >= limit:
                break
        # Fill remaining with first entries
        if len(result) < limit:
            existing_ids = {e.pk for e in result}
            for entry in cls.objects.exclude(pk__in=existing_ids)[:limit - len(result)]:
                result.append(entry)
        return result
