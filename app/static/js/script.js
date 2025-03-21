document.addEventListener("DOMContentLoaded", function () {
    let currentPage = localStorage.getItem("currentPage") || 1

    const container = document.querySelector("#container-product")
    const paginationNumbers = document.querySelector("#pagination-numbers")
    const previousLink = document.querySelector("#previous-link")
    const nextLink = document.querySelector("#next-link")

    const searchInput = document.getElementById("search-input")
    const searchButton = document.getElementById("search-btn")
    const productContainer = document.getElementById("container-product")

    async function fetchProducts(page) {
        try {
            const response = await fetch(`/api/products?page=${page}`)
            const data = await response.json()
    
            if (data.error) {
                console.error("Erreur lors du chargement des produits :", data.error)
                return
            }
    
            currentPage = data.current_page
            localStorage.setItem("currentPage", currentPage)
    
            renderProducts(data.products)
            renderPagination(data.total_pages)
    
            document.getElementById("pagination").style.display = "block"
        } catch (error) {
            console.error("Erreur JSON ou réseau :", error)
        }
    }
    

    function renderProducts(products) {
        container.innerHTML = products.map(product => `
            <div class="productCard">
                <a href="/${product.name}" class="Card" data-page="${currentPage}">
                    <div class="futureImg"> 
                        <img src="../static/images/image.webp"" alt="Description de l'image">
                    </div>
                    <div class="fastInformations">
                        <p>Nom : ${product.name}</p>
                        <p>Marque : ${product.brand}</p>
                        <p>Volume : ${product.volume}</p>
                        <p>Catégorie : ${product.categorie}</p>
                    </div>
                </a>
            </div>
        `).join('')
    }

    function renderPagination(totalPages) {
        paginationNumbers.innerHTML = ""
        if (currentPage <= 1) {
            previousLink.disabled = true
            previousLink.style.opacity = "0.5"
        } else {
            previousLink.disabled = false
            previousLink.style.opacity = "1"
        }
    
        if (currentPage >= totalPages) {
            nextLink.disabled = true
            nextLink.style.opacity = "0.5"
        } else {
            nextLink.disabled = false
            nextLink.style.opacity = "1"
        }
        for (let i = 1; i <= totalPages; i++) {
            const aLink = document.createElement("a")
            aLink.textContent = i
            aLink.className = "pagination-btn"
            aLink.dataset.page = i
            if (i == currentPage) aLink.style.fontWeight = "bold"
            paginationNumbers.appendChild(aLink)
        }
    }

    document.body.addEventListener("click", async (e) => {
        if (e.target.matches(".pagination-btn")) {
            let page = e.target.dataset.page
            await fetchProducts(page)
        } else if (e.target.matches("#previous-link") && currentPage > 1) {
            await fetchProducts(currentPage - 1)
        } else if (e.target.matches("#next-link")) {
            await fetchProducts(Number(currentPage) + 1)
        } else if (e.target.closest(".Card")) {
            localStorage.setItem("currentPage", currentPage)
        }
    })

    fetchProducts(currentPage)

    
    async function searchProducts() {
        const query = searchInput.value.trim()
        if (query === "") return
    
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`)
        const products = await response.json()
    
        productContainer.innerHTML = ""
    
        document.getElementById("pagination").style.display = "none"
    
        if (products.length === 0) {
            productContainer.innerHTML = "<p>Aucun produit trouvé.</p>"
            return
        }
    
        products.forEach(product => {
            productContainer.innerHTML += `
                <div class="productCard">
                    <a href="/${product.name}" class="Card"> 
                        <div class="futureImg">
                            <img src="../static/images/image.jpg" alt="Description de l'image">
                        </div>
                        <div class="fastInformations">
                            <p>Nom : ${product.name}</p>
                            <p>Marque : ${product.brand}</p>
                            <p>Volume : ${product.volume}</p>
                            <p>Catégorie : ${product.categorie}</p>
                        </div>
                    </a>
                </div>
            `
        })
    }
    

    searchButton.addEventListener("click", searchProducts)
    searchInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") searchProducts()
    })
})
