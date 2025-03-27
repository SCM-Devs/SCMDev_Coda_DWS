document.addEventListener("DOMContentLoaded", function () {
    let currentSearchPage = 1
    let currentPage =  1

    const container = document.querySelector("#container-product")
    const paginationNumbers = document.querySelector("#pagination-numbers")
    const previousLink = document.querySelector("#previous-link")
    const nextLink = document.querySelector("#next-link")

    const searchInput = document.getElementById("search-input")
    const searchButton = document.getElementById("search-btn")
    const productContainer = document.getElementById("container-product")

    const mainLink = document.getElementById("main-link")
    const pagination = document.getElementById("pagination")
    const searchPagination = document.getElementById("search-pagination")


    function getQueryParam(param, defaultValue) {
        const url = window.location.search
        const params = new URLSearchParams(url)
        const value = params.get(param)
        if (value === null) {
            return defaultValue
        }
        return value
    }

    function setQueryParam(param, value) {
        const url = new URL(window.location)
        const params = url.searchParams
    
        if (param === "searchPage") {
            params.delete("page")
            params.set("searchPage", value)
        } else if (param === "page") {
            params.delete("searchPage")
            params.set("page", value)
        }
    
        window.history.replaceState({}, "", url.pathname + "?" + params.toString())
    }
    

    function isSearching() {
        const url = window.location.search
        const params = new URLSearchParams(url)
        return params.has("q")
    }



    async function fetchProducts(page) {
        try {
            const response = await fetch(`/api/products?page=${page}`)
            const data = await response.json()
            console.log(data)
            if (data.error) {
                console.error("Erreur lors du chargement des produits :", data.error)
                return
            }
    
            currentPage = data.current_page
            setQueryParam("page", currentPage)

    
            renderProducts(data.products)
            renderPagination(data.total_pages)

            pagination.style.display = "flex"
            searchPagination.style.display = "none"

    
        } catch (error) {
            console.error("Erreur JSON ou réseau :", error)
        }
    }
    
     async function fetchSearchResults(page) {
         const query = searchInput.value.trim()

         if (!query) {
             console.error("champ recherche vide")
             return
         }

         try {
             const response = await fetch(`/search?q=${query}&page=${page}`)
             const data = await response.json()
             if (data.error) {
                 console.error("Erreur chargement res recherche", data.error)
                 return
             }
             currentSearchPage = data.current_page
             setQueryParam("searchPage", currentSearchPage)
             pagination.style.display = "none"

             searchPagination.style.display = "block"


             renderProducts(data.products)
             renderSearchPagination(data.total_pages)
         } catch (error) {
             console.error("eeurur réseau", error)
         }
     }


    function renderProducts(products) {
        //mettre qd recherche lapage recherhce pour lien éventuel ??
        container.innerHTML = products.map(product => `
            <div class="productCard">
                <a href="/${product.name}" class="Card" data-page="${currentPage}">
                    <div class="futureImg"> 
                        <img src="../static/images/${product.image_url}" alt="Description de l'image">
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
            const aLink = document.createElement("a")
            aLink.textContent = i
            aLink.className = "pagination-btn"
            aLink.dataset.page = i

            if (i == currentPage) {
                aLink.style.fontWeight = "bold"
            }

            paginationNumbers.appendChild(aLink)
        }
    }
    
    function renderSearchPagination(totalPages) {
        searchPagination.innerHTML = ""
        const startPage = Math.max(1, currentSearchPage - 2)
        const endPage = Math.min(totalPages, startPage + 4)
    
        const prevButton = document.createElement("a")
        prevButton.innerText = "Précédent"
        prevButton.style.opacity = currentSearchPage > 1 ? "1" : "0.5"
        prevButton.addEventListener("click", function (e) {
            e.preventDefault()
            if (currentSearchPage > 1) fetchSearchResults(currentSearchPage - 1)
        })
        searchPagination.appendChild(prevButton)
    
        for (let i = startPage; i <= endPage; i++) {
            const pageLink = document.createElement("a")
            pageLink.innerText = i
            pageLink.className = "pagination-btn"
            if (i === currentSearchPage) pageLink.style.fontWeight = "bold"
    
            pageLink.addEventListener("click", function (e) {
                e.preventDefault()
                fetchSearchResults(i)
            })
    
            searchPagination.appendChild(pageLink)
        }
    
        const nextButton = document.createElement("a")
        nextButton.innerText = "Suivant"
        nextButton.style.opacity = currentSearchPage < totalPages ? "1" : "0.5"
        nextButton.addEventListener("click", function (e) {
            e.preventDefault()
            if (currentSearchPage < totalPages) fetchSearchResults(currentSearchPage + 1)
        })
        searchPagination.appendChild(nextButton)
    }
    


    mainLink.addEventListener("click", async (e) => {
        e.preventDefault()
        setQueryParam("page", 1)
        searchInput.value = ""

        await fetchProducts(1)
    })

    document.body.addEventListener("click", async (e) => {
        if (e.target.matches(".pagination-btn")) {
            const page = e.target.dataset.page
             if (isSearching()) {
                 await fetchSearchResults(page)
             } else {
                await fetchProducts(page)
             }
        } else if (e.target.matches("#previous-link") && currentPage > 1) {
            const page = currentPage - 1
             if (isSearching()) {
                 await fetchSearchResults(page)
             } else {
                await fetchProducts(page)
             }
        } else if (e.target.matches("#next-link")) {
            const page = currentPage + 1
             if (isSearching()) {
                 await fetchSearchResults(page)
             } else {
                 await fetchProducts(page)
             }
        }
    })

    searchButton.addEventListener("click", () => {
        setQueryParam("searchPage", 1)
        fetchSearchResults(1)
    })

    searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            setQueryParam("searchPage", 1)
            fetchSearchResults(1)
        }
    })

     if (isSearching()) {
         fetchSearchResults(currentSearchPage)
     } else {
        fetchProducts(currentPage)
     }

      

})