class MediaSearch {
    constructor(options) {
        this.searchForm = document.getElementById('searchForm');
        this.searchResults = document.getElementById('searchResults');
        this.template = document.getElementById('mediaCardTemplate');
        this.searchUrl = options.searchUrl;
        this.addUrl = options.addUrl;
        this.type = options.type; // 'book' or 'show'
        this.formatResult = options.formatResult;
        
        this.init();
    }

    init() {
        this.searchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = document.getElementById('searchQuery').value;
            await this.performSearch(query);
        });
    }

    async performSearch(query) {
        try {
            const response = await fetch(`${this.searchUrl}?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.searchResults.innerHTML = '';
            
            const results = this.type === 'book' ? data.books : data.results;
            results.forEach(item => {
                const card = this.template.content.cloneNode(true);
                this.formatResult(card, item);
                this.searchResults.appendChild(card);
            });
        } catch (error) {
            console.error('Error:', error);
        }
    }
} 