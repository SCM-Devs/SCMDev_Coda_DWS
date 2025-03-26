document.addEventListener("DOMContentLoaded", function () {
    let currentPage = localStorage.getItem("currentPage") || 1

    const container = document.querySelector("#container-product")
    const paginationNumbers = document.querySelector("#pagination-numbers")
    const previousLink = document.querySelector("#previous-link")
    const nextLink = document.querySelector("#next-link")

    const searchInput = document.getElementById("search-input")
    const searchButton = document.getElementById("search-btn")
    const productContainer = document.getElementById("container-product")

    const mainLink = document.getElementById("main-link")

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
    
        previousLink.disabled = currentPage <= 1
        previousLink.style.opacity = currentPage <= 1 ? "0.5" : "1"
    
        nextLink.disabled = currentPage >= totalPages
        nextLink.style.opacity = currentPage >= totalPages ? "0.5" : "1"
    
        let startPage = Math.max(1, currentPage - 2) 
        let endPage = Math.min(totalPages, currentPage + 2)
    
        if (currentPage <= 2) {
            endPage = Math.min(totalPages, 5)
        } else if (currentPage >= totalPages - 1) {
            startPage = Math.max(1, totalPages - 4)
        }
    
        for (let i = startPage; i <= endPage; i++) {
            const btn = document.createElement("button")
            btn.textContent = i
            btn.className = "pagination-btn"
            btn.dataset.page = i
    
            if (i == currentPage) {
                btn.style.fontWeight = "bold"
            }
    
            paginationNumbers.appendChild(btn)
        }
    }
    
    mainLink.addEventListener("click", async (e) => {
        e.preventDefault()
    
        currentPage = 1
        localStorage.setItem("currentPage", currentPage)
        
        await fetchProducts(1)
    });
      

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
                            <img src="../static/images/image.webp" alt="Description de l'image">
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
