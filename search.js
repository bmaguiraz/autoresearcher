(function() {
  let searchIndex = null;
  let searchInput = null;
  let resultsContainer = null;

  async function loadSearchIndex() {
    if (searchIndex) return searchIndex;
    try {
      const response = await fetch('search-index.json');
      searchIndex = await response.json();
      return searchIndex;
    } catch (e) {
      console.error('Failed to load search index:', e);
      return [];
    }
  }

  function escapeRegex(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  function createHighlightedText(text, query) {
    const container = document.createDocumentFragment();
    if (!query) {
      container.appendChild(document.createTextNode(text));
      return container;
    }

    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    const parts = text.split(regex);

    for (const part of parts) {
      if (part.toLowerCase() === query.toLowerCase()) {
        const mark = document.createElement('mark');
        mark.textContent = part;
        container.appendChild(mark);
      } else {
        container.appendChild(document.createTextNode(part));
      }
    }
    return container;
  }

  function search(query) {
    if (!searchIndex || !query.trim()) return [];

    const normalizedQuery = query.toLowerCase().trim();
    const results = [];

    for (const doc of searchIndex) {
      const titleMatch = doc.title.toLowerCase().includes(normalizedQuery);
      const contentMatch = doc.content.includes(normalizedQuery);

      if (titleMatch || contentMatch) {
        let snippet = doc.preview;

        if (contentMatch && !titleMatch) {
          const idx = doc.content.indexOf(normalizedQuery);
          const start = Math.max(0, idx - 50);
          const end = Math.min(doc.content.length, idx + normalizedQuery.length + 100);
          snippet = (start > 0 ? '...' : '') +
                    doc.content.slice(start, end) +
                    (end < doc.content.length ? '...' : '');
        }

        results.push({
          url: doc.url,
          title: doc.title,
          snippet: snippet,
          score: titleMatch ? 2 : 1
        });
      }
    }

    results.sort((a, b) => b.score - a.score);
    return results;
  }

  function renderResults(results, query) {
    if (!resultsContainer) return;

    resultsContainer.replaceChildren();

    if (!query.trim()) {
      resultsContainer.style.display = 'none';
      return;
    }

    resultsContainer.style.display = 'block';

    if (results.length === 0) {
      const noResults = document.createElement('div');
      noResults.className = 'search-no-results';
      noResults.textContent = 'No results found';
      resultsContainer.appendChild(noResults);
      return;
    }

    for (const r of results) {
      const link = document.createElement('a');
      link.href = r.url;
      link.className = 'search-result';

      const title = document.createElement('div');
      title.className = 'search-result-title';
      title.appendChild(createHighlightedText(r.title, query));

      const snippet = document.createElement('div');
      snippet.className = 'search-result-snippet';
      snippet.appendChild(createHighlightedText(r.snippet, query));

      link.appendChild(title);
      link.appendChild(snippet);
      resultsContainer.appendChild(link);
    }
  }

  function handleSearch() {
    const query = searchInput.value;
    const results = search(query);
    renderResults(results, query);
  }

  function handleClickOutside(e) {
    if (resultsContainer &&
        !resultsContainer.contains(e.target) &&
        e.target !== searchInput) {
      resultsContainer.style.display = 'none';
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape' && resultsContainer) {
      resultsContainer.style.display = 'none';
      searchInput.blur();
    }
  }

  async function init() {
    searchInput = document.getElementById('docs-search');
    resultsContainer = document.getElementById('search-results');

    if (!searchInput || !resultsContainer) return;

    await loadSearchIndex();

    searchInput.addEventListener('input', handleSearch);
    searchInput.addEventListener('focus', handleSearch);
    document.addEventListener('click', handleClickOutside);
    document.addEventListener('keydown', handleKeydown);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
