document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("form-product")

    form.addEventListener("submit", function(e) {
        const id = document.getElementById("id").value
        console.log("Valeur du matériau : ", document.querySelector("#material-value").value)

        if (!id.trim()) {
            e.preventDefault()
            alert("Veuillez remplir tous les champs obligatoires !")
        } else {
            alert("Données enregistrées avec succès !")
        }
    })
})
