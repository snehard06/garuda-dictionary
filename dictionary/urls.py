"""
URL patterns for the dictionary app.
"""

from django.urls import path
from . import views

app_name = 'dictionary'

urlpatterns = [
    # Page views
    path('', views.home, name='home'),
    path('search/', views.search_results, name='search'),
    path('word/<int:pk>/', views.word_detail, name='word_detail'),
    path('explore/', views.explore, name='explore'),
    path('about/', views.about, name='about'),

    # API endpoints
    path('api/search/', views.api_search, name='api_search'),
    path('api/suggestions/', views.api_suggestions, name='api_suggestions'),
]
