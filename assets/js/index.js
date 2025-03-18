function handleRoleChange() {
    const dropdown = document.getElementById('role-dropdown');
    const selectedValue = dropdown.value;

    if (selectedValue === 'logout') {
        // Redirige vers la page de connexion
        window.location.href = 'login.html'; 
    }
}

// Ajout des événements pour les boutons URL et EAN
document.getElementById('name-btn').addEventListener('click', function() {
    this.classList.add('active');
    document.getElementById('ean-btn').classList.remove('active');
});

document.getElementById('ean-btn').addEventListener('click', function() {
    this.classList.add('active');
    document.getElementById('name-btn').classList.remove('active');
});

// Écouteur d'événements pour retirer l'option de déconnexion
document.getElementById('role-dropdown').addEventListener('change', function() {
    if (this.value === 'logout') {
        // Retirer l'option de déconnexion
        const option = this.querySelector('option[value="logout"]');
        if (option) {
            option.remove();
        }
    }
});