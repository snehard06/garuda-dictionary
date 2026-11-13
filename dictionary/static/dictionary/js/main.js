/**
 * Garuda Dictionary – Main JavaScript
 * Garuda Prakashan × Rishihood University Live Project
 *
 * Features:
 * - Live autocomplete with debounce
 * - Keyboard navigation (arrow keys, Enter, Escape)
 * - Copy-to-clipboard
 * - Web Share API with clipboard fallback
 * - Mobile navigation toggle
 * - Navbar scroll behaviour
 * - Search hint quick-fill
 */

'use strict';

/* ═══════════════════════════════════════════════════════════════
   UTILITY FUNCTIONS
═══════════════════════════════════════════════════════════════ */

/**
 * Returns a debounced version of `fn` that delays its execution by `wait` ms.
 */
function debounce(fn, wait) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), wait);
  };
}

/**
 * Shows a toast notification at the bottom-right corner.
 * @param {string} message
 * @param {number} duration – milliseconds before auto-dismiss
 */
function showToast(message, duration = 2500) {
  // Remove any existing toast
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.setAttribute('role', 'status');
  toast.setAttribute('aria-live', 'polite');
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 300ms ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ═══════════════════════════════════════════════════════════════
   NAVBAR
═══════════════════════════════════════════════════════════════ */

function initNavbar() {
  const navbar = document.getElementById('main-navbar');
  if (!navbar) return;

  // Scroll shadow
  const onScroll = () => {
    navbar.classList.toggle('scrolled', window.scrollY > 10);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile toggle
  const toggle = document.getElementById('nav-toggle');
  const navLinks = document.getElementById('nav-links');
  if (!toggle || !navLinks) return;

  toggle.addEventListener('click', () => {
    const isOpen = navLinks.classList.toggle('open');
    toggle.classList.toggle('open', isOpen);
    toggle.setAttribute('aria-expanded', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close nav on link click (mobile)
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      navLinks.classList.remove('open');
      toggle.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Active link highlighting
  const path = window.location.pathname;
  navLinks.querySelectorAll('a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === path || (href !== '/' && path.startsWith(href))) {
      link.classList.add('active');
    }
  });
}

/* ═══════════════════════════════════════════════════════════════
   AUTOCOMPLETE
═══════════════════════════════════════════════════════════════ */

class Autocomplete {
  /**
   * @param {HTMLInputElement} input – the search input element
   * @param {HTMLElement} dropdown – the dropdown container
   * @param {string} apiUrl – the suggestions API endpoint
   */
  constructor(input, dropdown, apiUrl) {
    this.input = input;
    this.dropdown = dropdown;
    this.apiUrl = apiUrl;
    this.activeIndex = -1;
    this.suggestions = [];
    this.abortController = null;

    this._bindEvents();
  }

  _bindEvents() {
    // Debounced input handler
    this.input.addEventListener('input', debounce((e) => {
      const q = e.target.value.trim();
      if (q.length === 0) {
        this.close();
        return;
      }
      this._fetchSuggestions(q);
    }, 280));

    // Keyboard navigation
    this.input.addEventListener('keydown', (e) => {
      if (!this.isOpen()) return;

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault();
          this._moveActive(1);
          break;
        case 'ArrowUp':
          e.preventDefault();
          this._moveActive(-1);
          break;
        case 'Enter':
          if (this.activeIndex >= 0) {
            e.preventDefault();
            this._selectItem(this.activeIndex);
          }
          break;
        case 'Escape':
          this.close();
          this.input.blur();
          break;
      }
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
        this.close();
      }
    });

    // ARIA
    this.input.setAttribute('autocomplete', 'off');
    this.input.setAttribute('aria-autocomplete', 'list');
    this.input.setAttribute('aria-haspopup', 'listbox');
    this.dropdown.setAttribute('role', 'listbox');
  }

  async _fetchSuggestions(query) {
    // Cancel previous request
    if (this.abortController) this.abortController.abort();
    this.abortController = new AbortController();

    this._showLoading();

    try {
      const url = `${this.apiUrl}?q=${encodeURIComponent(query)}`;
      const resp = await fetch(url, { signal: this.abortController.signal });
      if (!resp.ok) throw new Error('API error');
      const data = await resp.json();
      this.suggestions = data.suggestions || [];
      this._render();
    } catch (err) {
      if (err.name === 'AbortError') return; // Expected
      this._showEmpty('Could not load suggestions.');
    }
  }

  _render() {
    this.activeIndex = -1;
    this.dropdown.innerHTML = '';

    if (this.suggestions.length === 0) {
      this._showEmpty();
      return;
    }

    this.suggestions.forEach((s, i) => {
      const item = document.createElement('div');
      item.className = 'autocomplete-item';
      item.setAttribute('role', 'option');
      item.setAttribute('id', `suggestion-${i}`);
      item.setAttribute('aria-selected', 'false');
      item.innerHTML = `
        <span class="autocomplete-item__word" lang="hi">${this._escHtml(s.devanagari)}</span>
        <span class="autocomplete-item__romanised">${this._escHtml(s.romanised)}</span>
        <span class="autocomplete-item__meaning">${this._escHtml(s.meaning)}</span>
      `;
      item.addEventListener('click', () => this._selectItem(i));
      item.addEventListener('mouseenter', () => {
        this._setActive(i);
      });
      this.dropdown.appendChild(item);
    });

    this.dropdown.style.display = 'block';
  }

  _showLoading() {
    this.dropdown.innerHTML = `<div class="autocomplete-loading"><span class="spinner"></span></div>`;
    this.dropdown.style.display = 'block';
  }

  _showEmpty(msg = 'No suggestions found.') {
    this.dropdown.innerHTML = `<div class="autocomplete-empty">${this._escHtml(msg)}</div>`;
    this.dropdown.style.display = 'block';
  }

  _moveActive(dir) {
    const items = this.dropdown.querySelectorAll('.autocomplete-item');
    if (!items.length) return;

    this.activeIndex = Math.max(-1, Math.min(items.length - 1, this.activeIndex + dir));
    this._setActive(this.activeIndex);
  }

  _setActive(idx) {
    const items = this.dropdown.querySelectorAll('.autocomplete-item');
    items.forEach((el, i) => {
      const isActive = i === idx;
      el.classList.toggle('active', isActive);
      el.setAttribute('aria-selected', isActive ? 'true' : 'false');
    });
    this.activeIndex = idx;

    if (idx >= 0) {
      this.input.setAttribute('aria-activedescendant', `suggestion-${idx}`);
    } else {
      this.input.removeAttribute('aria-activedescendant');
    }
  }

  _selectItem(idx) {
    const s = this.suggestions[idx];
    if (!s) return;

    // Navigate to word detail page
    window.location.href = `/word/${s.id}/`;
  }

  isOpen() {
    return this.dropdown.style.display === 'block';
  }

  close() {
    this.dropdown.style.display = 'none';
    this.dropdown.innerHTML = '';
    this.activeIndex = -1;
    this.suggestions = [];
  }

  _escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}

/* ═══════════════════════════════════════════════════════════════
   SEARCH HINTS (clickable example words)
═══════════════════════════════════════════════════════════════ */

function initSearchHints() {
  document.querySelectorAll('.search-hint').forEach(hint => {
    hint.addEventListener('click', () => {
      const searchInput = document.querySelector('.search-form__input');
      if (!searchInput) return;
      searchInput.value = hint.textContent.trim();
      searchInput.focus();
      // Trigger input event for autocomplete
      searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    });
  });
}

/* ═══════════════════════════════════════════════════════════════
   COPY TO CLIPBOARD
═══════════════════════════════════════════════════════════════ */

function initCopyButtons() {
  document.querySelectorAll('[data-copy]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const textToCopy = btn.getAttribute('data-copy');
      if (!textToCopy) return;

      try {
        await navigator.clipboard.writeText(textToCopy);
        showToast('✓ Copied to clipboard');
      } catch {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = textToCopy;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showToast('✓ Copied to clipboard');
      }
    });
  });
}

/* ═══════════════════════════════════════════════════════════════
   WEB SHARE API
═══════════════════════════════════════════════════════════════ */

function initShareButtons() {
  document.querySelectorAll('[data-share]').forEach(btn => {
    const wordName = btn.getAttribute('data-share-title') || document.title;
    const wordUrl = btn.getAttribute('data-share-url') || window.location.href;
    const wordText = btn.getAttribute('data-share-text') || '';

    if (!navigator.share) {
      // Replace with copy-URL fallback
      btn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(wordUrl);
          showToast('🔗 Link copied to clipboard');
        } catch {
          showToast('Could not copy link');
        }
      });
      return;
    }

    btn.addEventListener('click', async () => {
      try {
        await navigator.share({
          title: wordName,
          text: wordText,
          url: wordUrl,
        });
      } catch (err) {
        if (err.name !== 'AbortError') {
          showToast('Could not share word');
        }
      }
    });
  });
}

/* ═══════════════════════════════════════════════════════════════
   EXPLORE PAGE – FILTER ACTIVE STATES
═══════════════════════════════════════════════════════════════ */

function initExploreFilters() {
  // Letter and POS filters are handled server-side, but we keep the
  // current active state from query params for visual feedback.
  const params = new URLSearchParams(window.location.search);
  const letter = (params.get('letter') || '').toUpperCase();
  const pos = params.get('pos') || '';

  document.querySelectorAll('.letter-btn').forEach(btn => {
    if (btn.dataset.letter === letter) btn.classList.add('active');
  });

  document.querySelectorAll('.pos-filter-btn').forEach(btn => {
    if (btn.dataset.pos === pos) btn.classList.add('active');
  });
}

/* ═══════════════════════════════════════════════════════════════
   SCROLL ANIMATIONS (Intersection Observer)
═══════════════════════════════════════════════════════════════ */

function initScrollAnimations() {
  if (!('IntersectionObserver' in window)) return;

  const elements = document.querySelectorAll(
    '.word-card, .step-card, .result-card, .wotd-card, .sidebar-card'
  );

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  elements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });
}

/* ═══════════════════════════════════════════════════════════════
   INITIALISE ALL FEATURES
═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  // Core navigation
  initNavbar();

  // Autocomplete – initialise on any page that has a search input + dropdown
  const searchInput = document.getElementById('search-input');
  const autocompleteDropdown = document.getElementById('autocomplete-dropdown');
  if (searchInput && autocompleteDropdown) {
    new Autocomplete(searchInput, autocompleteDropdown, '/api/suggestions/');
  }

  // Search hints
  initSearchHints();

  // Copy buttons
  initCopyButtons();

  // Share buttons
  initShareButtons();

  // Explore page filters
  initExploreFilters();

  // Subtle scroll animations
  initScrollAnimations();
});
