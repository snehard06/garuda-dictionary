"""
Django Admin configuration for Garuda Dictionary.
"""

from django.contrib import admin
from .models import DictionaryEntry


@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(admin.ModelAdmin):
    """Admin interface for dictionary entries with search and filter support."""

    list_display = (
        'devanagari_word', 'romanised_word', 'english_meaning',
        'part_of_speech', 'is_demo_entry', 'created_at'
    )
    list_filter = ('part_of_speech', 'is_demo_entry', 'created_at')
    search_fields = (
        'devanagari_word', 'romanised_word', 'alternate_romanisations',
        'english_meaning', 'definition'
    )
    ordering = ('romanised_word',)
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Core Word', {
            'fields': ('devanagari_word', 'romanised_word', 'alternate_romanisations', 'english_meaning')
        }),
        ('Linguistic Details', {
            'fields': ('part_of_speech', 'definition', 'example_sentence', 'example_translation')
        }),
        ('Etymology & Sources', {
            'fields': ('etymology', 'source_reference'),
            'classes': ('collapse',),
        }),
        ('Metadata', {
            'fields': ('is_demo_entry', 'created_at'),
        }),
    )
