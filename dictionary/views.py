"""
Views for Garuda Dictionary.

Handles:
- Homepage with word of day and popular words
- Search results page
- Word detail page
- Explore/browse page
- About page
- API endpoints: /api/search/ and /api/suggestions/
"""

import json
import unicodedata

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET

from .models import DictionaryEntry


# ── Page views ────────────────────────────────────────────────────────────────

def home(request):
    """
    Homepage: hero section, search, word of day, popular words.
    If a 'q' param is present, perform search and display results inline.
    """
    query = request.GET.get('q', '').strip()
    context = {
        'word_of_day': DictionaryEntry.get_word_of_day(),
        'popular_words': DictionaryEntry.get_popular_words(12),
        'query': query,
    }

    if query:
        results = DictionaryEntry.search(query)
        context['results'] = results
        context['result_count'] = len(results)

    return render(request, 'dictionary/home.html', context)


def search_results(request):
    """
    Dedicated search results page for non-JS fallback and direct links.
    """
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = DictionaryEntry.search(query)

    context = {
        'query': query,
        'results': results,
        'result_count': len(results),
    }
    return render(request, 'dictionary/search_results.html', context)


def word_detail(request, pk):
    """
    Full detail page for a single dictionary entry.
    Includes related words based on English meaning keywords.
    """
    entry = get_object_or_404(DictionaryEntry, pk=pk)

    # Find related words: entries that share keywords in english_meaning
    related = []
    keywords = entry.english_meaning.lower().replace(',', ' ').split()
    seen = {entry.pk}
    for keyword in keywords[:3]:
        for candidate in DictionaryEntry.objects.filter(
            english_meaning__icontains=keyword
        ).exclude(pk__in=seen)[:4]:
            if candidate.pk not in seen:
                seen.add(candidate.pk)
                related.append(candidate)
        if len(related) >= 6:
            break

    context = {
        'entry': entry,
        'related': related[:6],
        'alts': entry.get_alternate_romanisations_list(),
    }
    return render(request, 'dictionary/word_detail.html', context)


def explore(request):
    """
    Explore / browse page: alphabetical listing with filters and pagination.
    """
    query = request.GET.get('q', '').strip()
    pos_filter = request.GET.get('pos', '').strip()
    letter_filter = request.GET.get('letter', '').strip()

    entries = DictionaryEntry.objects.all().order_by('romanised_word')

    if query:
        entries = DictionaryEntry.search(query)
        # search() returns a list; wrap for Paginator
        paginator = Paginator(entries, 20)
    else:
        if pos_filter:
            entries = entries.filter(part_of_speech=pos_filter)
        if letter_filter:
            # Filter by starting Devanagari character or romanised first letter
            entries = entries.filter(romanised_word__istartswith=letter_filter)
        paginator = Paginator(entries, 20)

    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    pos_choices = DictionaryEntry.PART_OF_SPEECH_CHOICES
    # English alphabet letters for filter
    letters = list('abcdefghijklmnopqrstuvwxyz'.upper())

    context = {
        'page_obj': page_obj,
        'query': query,
        'pos_filter': pos_filter,
        'letter_filter': letter_filter.upper(),
        'pos_choices': pos_choices,
        'letters': letters,
        'total_count': DictionaryEntry.objects.count(),
    }
    return render(request, 'dictionary/explore.html', context)


def about(request):
    """About page – project attribution and information."""
    context = {
        'total_count': DictionaryEntry.objects.count(),
    }
    return render(request, 'dictionary/about.html', context)


# ── API endpoints ─────────────────────────────────────────────────────────────

@require_GET
def api_search(request):
    """
    GET /api/search/?q=<query>

    Returns JSON search results.
    """
    query = request.GET.get('q', '').strip()

    # Input validation
    if not query:
        return JsonResponse({'error': 'Query parameter q is required.', 'results': []}, status=400)
    if len(query) > 200:
        return JsonResponse({'error': 'Query too long.', 'results': []}, status=400)

    results = DictionaryEntry.search(query)

    data = [{
        'id': e.pk,
        'devanagari_word': e.devanagari_word,
        'romanised_word': e.romanised_word,
        'english_meaning': e.english_meaning,
        'part_of_speech': e.part_of_speech,
        'definition': e.definition,
        'example_sentence': e.example_sentence,
        'example_translation': e.example_translation,
    } for e in results]

    return JsonResponse({'query': query, 'count': len(data), 'results': data})


@require_GET
def api_suggestions(request):
    """
    GET /api/suggestions/?q=<query>

    Returns lightweight autocomplete suggestions.
    """
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'suggestions': []})
    if len(query) > 100:
        return JsonResponse({'suggestions': []})

    suggestions = DictionaryEntry.get_suggestions(query, limit=8)
    return JsonResponse({'query': query, 'suggestions': suggestions})
