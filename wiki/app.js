// Wiki pages registry
const PAGES = [
    'Home',
    'Getting-Started',
    'Architecture',
    'Configuration',
    'Agents',
    'Tools',
    'Development-Guide'
];

// Cache for loaded pages
const pageCache = {};

// State
let currentPage = 'Home';
let allPagesContent = {};

// DOM elements
const article = document.getElementById('article');
const nav = document.getElementById('nav');
const tocNav = document.getElementById('toc-nav');
const sidebar = document.getElementById('sidebar');
const menuBtn = document.getElementById('menu-btn');
const searchInput = document.getElementById('search-input');
const searchOverlay = document.getElementById('search-overlay');
const searchModalInput = document.getElementById('search-modal-input');
const searchResults = document.getElementById('search-results');

// Configure marked
marked.setOptions({
    gfm: true,
    breaks: false,
    headerIds: true,
    mangle: false
});

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
    // Load initial page from hash or default
    const hash = window.location.hash.slice(1);
    if (hash && PAGES.includes(hash)) {
        currentPage = hash;
    }

    // Set up navigation
    setupNavigation();
    setupSearch();
    setupMobileMenu();
    setupKeyboardShortcuts();

    // Load current page
    await loadPage(currentPage);

    // Preload all pages for search
    preloadAllPages();
}

function setupNavigation() {
    const navItems = nav.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            navigateTo(page);
        });
    });

    // Handle browser back/forward
    window.addEventListener('hashchange', () => {
        const hash = window.location.hash.slice(1);
        if (hash && PAGES.includes(hash) && hash !== currentPage) {
            navigateTo(hash, false);
        }
    });
}

function setupMobileMenu() {
    menuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Close sidebar on page navigate (mobile)
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Cmd/Ctrl + K to open search
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            openSearch();
        }
        // Escape to close search
        if (e.key === 'Escape') {
            closeSearch();
        }
    });
}

function setupSearch() {
    searchInput.addEventListener('focus', openSearch);

    searchOverlay.addEventListener('click', (e) => {
        if (e.target === searchOverlay) {
            closeSearch();
        }
    });

    searchModalInput.addEventListener('input', (e) => {
        performSearch(e.target.value);
    });
}

function openSearch() {
    searchOverlay.classList.add('active');
    searchModalInput.focus();
    searchModalInput.value = '';
    searchResults.innerHTML = '<div class="search-empty">Type to search across all wiki pages</div>';
}

function closeSearch() {
    searchOverlay.classList.remove('active');
    searchModalInput.value = '';
}

function performSearch(query) {
    if (!query.trim()) {
        searchResults.innerHTML = '<div class="search-empty">Type to search across all wiki pages</div>';
        return;
    }

    const results = [];
    const lowerQuery = query.toLowerCase();

    for (const [page, content] of Object.entries(allPagesContent)) {
        const lowerContent = content.toLowerCase();
        const idx = lowerContent.indexOf(lowerQuery);
        if (idx !== -1) {
            // Extract snippet around match
            const start = Math.max(0, idx - 60);
            const end = Math.min(content.length, idx + query.length + 60);
            let snippet = content.slice(start, end);
            if (start > 0) snippet = '...' + snippet;
            if (end < content.length) snippet = snippet + '...';

            // Highlight match
            const highlightedSnippet = snippet.replace(
                new RegExp(escapeRegex(query), 'gi'),
                '<mark>$&</mark>'
            );

            results.push({
                page,
                title: page.replace(/-/g, ' '),
                snippet: highlightedSnippet
            });
        }
    }

    if (results.length === 0) {
        searchResults.innerHTML = '<div class="search-empty">No results found</div>';
        return;
    }

    searchResults.innerHTML = results.map(r => `
        <div class="search-result-item" data-page="${r.page}">
            <div class="search-result-title">${r.title}</div>
            <div class="search-result-snippet">${r.snippet}</div>
        </div>
    `).join('');

    // Add click handlers
    searchResults.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', () => {
            navigateTo(item.dataset.page);
            closeSearch();
        });
    });
}

function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

async function navigateTo(page, updateHash = true) {
    if (updateHash) {
        window.location.hash = page;
    }
    currentPage = page;
    updateActiveNav();
    await loadPage(page);
    sidebar.classList.remove('open');
    window.scrollTo(0, 0);
}

function updateActiveNav() {
    nav.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === currentPage);
    });
}

async function loadPage(page) {
    article.innerHTML = '<div class="loading">Loading...</div>';

    try {
        const content = await fetchPage(page);
        const html = marked.parse(content);
        article.innerHTML = html;

        // Build table of contents
        buildTOC();

        // Add anchor links to headings
        addHeadingAnchors();

        // Intercept wiki links
        interceptLinks();
    } catch (err) {
        article.innerHTML = `
            <h1>Page Not Found</h1>
            <p>The page "${page}" could not be loaded.</p>
            <p><a href="#Home">Go to Home</a></p>
        `;
    }
}

async function fetchPage(page) {
    if (pageCache[page]) return pageCache[page];

    const response = await fetch(`${page}.md`);
    if (!response.ok) throw new Error('Page not found');

    const content = await response.text();
    pageCache[page] = content;
    return content;
}

async function preloadAllPages() {
    for (const page of PAGES) {
        try {
            const content = await fetchPage(page);
            allPagesContent[page] = content;
        } catch (e) {
            // Ignore load failures for search
        }
    }
}

function buildTOC() {
    const headings = article.querySelectorAll('h2, h3');
    if (headings.length === 0) {
        tocNav.innerHTML = '';
        return;
    }

    tocNav.innerHTML = Array.from(headings).map(h => {
        const id = h.id || slugify(h.textContent);
        h.id = id;
        const level = h.tagName === 'H3' ? 'level-3' : '';
        return `<a href="#${id}" class="toc-link ${level}">${h.textContent}</a>`;
    }).join('');

    // Scroll spy
    setupScrollSpy(headings);
}

function setupScrollSpy(headings) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = entry.target.id;
                    tocNav.querySelectorAll('.toc-link').forEach(link => {
                        link.classList.toggle('active', link.getAttribute('href') === `#${id}`);
                    });
                }
            });
        },
        { rootMargin: '-80px 0px -70% 0px' }
    );

    headings.forEach(h => observer.observe(h));
}

function addHeadingAnchors() {
    article.querySelectorAll('h1, h2, h3, h4').forEach(h => {
        if (!h.id) h.id = slugify(h.textContent);
    });
}

function interceptLinks() {
    article.querySelectorAll('a').forEach(link => {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('http') && !href.startsWith('#')) {
            // Internal wiki link
            const page = href.replace(/\.md$/, '').replace(/\(|\)/g, '');
            if (PAGES.includes(page)) {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    navigateTo(page);
                });
            }
        }
    });
}

function slugify(text) {
    return text
        .toLowerCase()
        .replace(/[^\w\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim();
}
