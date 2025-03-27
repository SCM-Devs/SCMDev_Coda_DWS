document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("form-product")

    form.addEventListener("submit", function(e) {
        const nameProduct = document.getElementById("name-product").value
        const visibleName = document.getElementById("nom_d_origine").value

        if (!nameProduct.trim() || !visibleName.trim()) {
            e.preventDefault()
            alert("Veuillez remplir tous les champs obligatoires !")
        } else {
            alert("Données enregistrées avec succès !")
        }
    })
})
