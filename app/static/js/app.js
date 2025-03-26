import { fetchProducts, fetchSearchResults } from './api.js';
import Pagination from './pagination.js';
import Product from './product.js';
import Search from './search.js';

class App {
    constructor() {
        this.currentPage = 1;
        this.currentSearchPage = 1;

        // Lire les paramètres de l'URL (page ou searchPage)
        const urlParams = new URLSearchParams(window.location.search);
        this.currentPage = parseInt(urlParams.get('page')) || 1;  // Utilise `page` par défaut
        this.currentSearchPage = parseInt(urlParams.get('searchPage')) || 1;  // Utilise `searchPage` par défaut

        // Initialiser la pagination
        this.pagination = new Pagination(this.currentPage, this.currentSearchPage);

        this.searchInput = document.getElementById("search-input");
        this.searchButton = document.getElementById("search-btn");
        this.search = new Search(this.searchInput, this.searchButton);

        this.search.handleSearch(this.fetchSearchResults.bind(this));
        this.fetchProducts(this.currentPage);
    }

    async fetchProducts(page) {
        const data = await fetchProducts(page);
        if (data) {
            this.currentPage = data.current_page;
            this.pagination.renderPagination(data.total_pages);
            this.renderProducts(data.products);
        }
    }

    async fetchSearchResults(query, page) {
        const data = await fetchSearchResults(query, page);
        if (data) {
            this.currentSearchPage = data.current_page;
            this.pagination.renderSearchPagination(data.total_pages);
            this.renderProducts(data.products);
        }
    }

    renderProducts(products) {
        const container = document.getElementById("container-product");
        container.innerHTML = products.map(product => new Product(product).render()).join('');
    }
}

new App();
