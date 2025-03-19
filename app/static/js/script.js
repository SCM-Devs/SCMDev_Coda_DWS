document.addEventListener("DOMContentLoaded", function () {
    fetch('/products')
        .then(response => response.json())
        .then(products => {
            const container = document.getElementById('container-product');
            products.forEach(product => {
                const productDiv = document.createElement('div');
                productDiv.classList.add('productCard');
                productDiv.innerHTML = `
                    <p>Nom : {{ product.name }}</p>
                    <p>Marque : {{ product.brand }}</p>
                    <p>Volume : {{ product.volume }}</p>
                    <p>Catégorie : {{ product.categorie }}</p>
                    <p>Poids net : {{ product.net_weight }}</p>
                `;
                container.appendChild(productDiv);
            });
        })
        .catch(error => console.error('Erreur:', error));
});
