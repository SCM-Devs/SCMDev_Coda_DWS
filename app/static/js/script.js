document.addEventListener("DOMContentLoaded", function () {
    let currentPage = localStorage.getItem("currentPage") || 1;

    const container = document.querySelector("#container-product");
    const paginationNumbers = document.querySelector("#pagination-numbers");
    const previousLink = document.querySelector("#previous-link");
    const nextLink = document.querySelector("#next-link");

    async function fetchProducts(page) {
        try {
            const response = await fetch(`/api/products?page=${page}`);
            const data = await response.json();

            if (data.error) {
                console.error("Erreur lors du chargement des produits :", data.error);
                return;
            }

            currentPage = data.current_page;
            localStorage.setItem("currentPage", currentPage);

            renderProducts(data.products);
            renderPagination(data.total_pages);
        } catch (error) {
            console.error("Erreur JSON ou réseau :", error);
        }
    }

    function renderProducts(products) {
        container.innerHTML = products.map(product => `
            <div class="productCard">
                <a href="/${product.name}" class="Card" data-page="${currentPage}">
                    <div class="futureImg"></div>
                    <div class="fastInformations">
                        <p>Nom : ${product.name}</p>
                        <p>Marque : ${product.brand}</p>
                        <p>Volume : ${product.volume}</p>
                        <p>Catégorie : ${product.categorie}</p>
                    </div>
                </a>
            </div>
        `).join('');
    }

    function renderPagination(totalPages) {
        paginationNumbers.innerHTML = "";
        for (let i = 1; i <= totalPages; i++) {
            const btn = document.createElement("button");
            btn.textContent = i;
            btn.className = "pagination-btn";
            btn.dataset.page = i;
            if (i == currentPage) btn.style.fontWeight = "bold";
            paginationNumbers.appendChild(btn);
        }
    }

    document.body.addEventListener("click", async (e) => {
        if (e.target.matches(".pagination-btn")) {
            let page = e.target.dataset.page;
            await fetchProducts(page);
        } else if (e.target.matches("#previous-link") && currentPage > 1) {
            await fetchProducts(currentPage - 1);
        } else if (e.target.matches("#next-link")) {
            await fetchProducts(Number(currentPage) + 1);
        } else if (e.target.closest(".Card")) {
            localStorage.setItem("currentPage", currentPage);
        }
    });

    fetchProducts(currentPage);
});
