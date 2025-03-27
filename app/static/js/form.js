document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("form-product")

    form.addEventListener("submit", function(e) {
        const visibleName = document.getElementById("nom_d_origine").value

        if (!visibleName.trim()) {
            e.preventDefault()
            alert("Veuillez remplir tous les champs obligatoires !")
        } else {
            alert("Données enregistrées avec succès !")
        }
    })
})
