document.getElementById('searchButton').addEventListener('click', function() {
    const ean = document.getElementById('eanInput').value.trim();
    if (ean) {
        // Envoyer une requête au serveur
        fetch(`https://votre-serveur.com/api/ean?code=${ean}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur réseau');
                }
                return response.json();
            })
            .then(data => {
                // Afficher les résultats
                displayResults(data);
            })
            .catch(error => {
                alert('Erreur : ' + error.message);
            });
    } else {
        alert('Veuillez entrer un EAN valide.');
    }
});

function displayResults(data) {
    // Créer un conteneur pour les résultats
    const resultContainer = document.createElement('div');
    resultContainer.className = 'result-container mt-4';

    // Créer un conteneur pour le produit
    const productContainer = document.createElement('div');
    productContainer.className = 'product-container';

    // Ajouter le nom du produit
    const productName = document.createElement('h2');
    productName.textContent = data.productName; // Assurez-vous que le nom du produit est dans la réponse
    productContainer.appendChild(productName);

    // Ajouter la marque du produit
    const productBrand = document.createElement('p');
    productBrand.innerHTML = `<strong>Marque :</strong> ${data.brand}`; // Assurez-vous que la marque est dans la réponse
    productContainer.appendChild(productBrand);

    // Ajouter le volume du produit
    const productVolume = document.createElement('p');
    productVolume.innerHTML = `<strong>Volume :</strong> ${data.volume}`; // Assurez-vous que le volume est dans la réponse
    productContainer.appendChild(productVolume);

    // Ajouter l'image du produit
    const productImage = document.createElement('img');
    productImage.src = data.imageUrl; // Assurez-vous que l'URL de l'image est dans la réponse
    productImage.alt = data.productName;
    productImage.className = 'product-image';
    productContainer.appendChild(productImage);

    // Ajouter le conteneur du produit aux résultats
    resultContainer.appendChild(productContainer);

    // Ajouter les résultats à la carte
    const cardBody = document.querySelector('.card-body');
    cardBody.appendChild(resultContainer);
}