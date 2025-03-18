const cardData = [
    { categorie: '', nom: '', marque: '', volume: '' },
    { categorie: '', nom: '', marque: '', volume: '' },
    { categorie: '', nom: '', marque: '', volume: '' }
];

const cardContainer = document.getElementById('card-container');

cardData.forEach(data => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
        <img src="https://placehold.co/256x192" alt="Placeholder image">
        <p>Categorie : ${data.categorie}</p>
        <p>Nom : ${data.nom}</p>
        <p>Marque : ${data.marque}</p>
        <p>Volume : ${data.volume}</p>
    `;
    cardContainer.appendChild(card);
});