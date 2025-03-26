export default class Pagination {
    constructor(currentPage = 1, currentSearchPage = 1) {
        this.currentPage = currentPage;  // page des produits
        this.currentSearchPage = currentSearchPage;  // page de recherche
    }

    renderPagination(totalPages) {
        const paginationNumbers = document.querySelector("#pagination-numbers");
        const previousLink = document.querySelector("#previous-link");
        const nextLink = document.querySelector("#next-link");

        paginationNumbers.innerHTML = "";
        previousLink.disabled = this.currentPage <= 1;
        nextLink.disabled = this.currentPage >= totalPages;

        let startPage = Math.max(1, this.currentPage - 2);
        let endPage = Math.min(totalPages, this.currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const pageLink = document.createElement("a");
            pageLink.textContent = i;
            pageLink.className = "pagination-btn";
            pageLink.dataset.page = i;
            if (i === this.currentPage) {
                pageLink.style.fontWeight = "bold";
            }
            pageLink.addEventListener("click", (e) => {
                e.preventDefault();
                this.handlePageChange(i); // changement de page
            });
            paginationNumbers.appendChild(pageLink);
        }
    }

    renderSearchPagination(totalPages) {
        const searchPagination = document.querySelector("#search-pagination");
        searchPagination.innerHTML = "";

        const startPage = Math.max(1, this.currentSearchPage - 2);
        const endPage = Math.min(totalPages, startPage + 4);

        const prevButton = document.createElement("a");
        prevButton.innerText = "Précédent";
        prevButton.style.opacity = this.currentSearchPage > 1 ? "1" : "0.5";
        prevButton.addEventListener("click", (e) => {
            e.preventDefault();
            if (this.currentSearchPage > 1) {
                this.handlePageChange(this.currentSearchPage - 1, true); // page de recherche
            }
        });
        searchPagination.appendChild(prevButton);

        for (let i = startPage; i <= endPage; i++) {
            const pageLink = document.createElement("a");
            pageLink.innerText = i;
            pageLink.className = "pagination-btn";
            if (i === this.currentSearchPage) {
                pageLink.style.fontWeight = "bold";
            }
            pageLink.addEventListener("click", (e) => {
                e.preventDefault();
                this.handlePageChange(i, true); // page de recherche
            });
            searchPagination.appendChild(pageLink);
        }

        const nextButton = document.createElement("a");
        nextButton.innerText = "Suivant";
        nextButton.style.opacity = this.currentSearchPage < totalPages ? "1" : "0.5";
        nextButton.addEventListener("click", (e) => {
            e.preventDefault();
            if (this.currentSearchPage < totalPages) {
                this.handlePageChange(this.currentSearchPage + 1, true); // page de recherche
            }
        });
        searchPagination.appendChild(nextButton);
    }

    handlePageChange(page, isSearch = false) {
        if (isSearch) {
            this.currentSearchPage = page;
            // Met à jour l'URL pour la recherche
            const url = new URL(window.location);
            url.searchParams.set('searchPage', page); // searchPage pour la recherche
            window.history.pushState({}, '', url);
        } else {
            this.currentPage = page;
            // Met à jour l'URL pour la pagination des produits
            const url = new URL(window.location);
            url.searchParams.set('page', page); // page pour les produits
            window.history.pushState({}, '', url);
        }

        // Rafraîchir les résultats
        window.dispatchEvent(new Event('popstate')); // Déclencher un événement pour charger les nouveaux résultats
    }
}
