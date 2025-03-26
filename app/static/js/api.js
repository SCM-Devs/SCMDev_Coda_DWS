export async function fetchProducts(page) {
    try {
        const response = await fetch(`/api/products?page=${page}`)
        const data = await response.json()
        console.log(data)
        if (data.error) {
            console.error("Erreur lors du chargement des produits :", data.error)
            return
        }
        return data

        // currentPage = data.current_page
        // setQueryParam("page", currentPage)


        // renderProducts(data.products)
        // renderPagination(data.total_pages)

        // pagination.style.display = "flex"
        // searchPagination.style.display = "none"


    } catch (error) {
        console.error("Erreur JSON ou réseau :", error)
    }
}

export async function fetchSearchResults(query, page) {
//     const query = searchInput.value.trim()
// //
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
        return data
        // currentSearchPage = data.current_page
        // setQueryParam("searchPage", currentSearchPage)
        // pagination.style.display = "none"

        // searchPagination.style.display = "block"


        // renderProducts(data.products)
        // renderSearchPagination(data.total_pages)
    } catch (error) {
        console.error("eeurur réseau", error)
    }
}