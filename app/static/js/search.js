export default class Search {
    constructor(searchInput, searchButton) {
        this.searchInput = searchInput;
        this.searchButton = searchButton;
    }

    handleSearch(fetchSearchResults) {
        this.searchButton.addEventListener("click", async () => {
            const query = this.searchInput.value.trim();
            if (query) {
                await fetchSearchResults(query, 1);
            }
        });

        this.searchInput.addEventListener("keydown", async (event) => {
            if (event.key === "Enter") {
                const query = this.searchInput.value.trim();
                if (query) {
                    await fetchSearchResults(query, 1);
                }
            }
        });
    }
}
