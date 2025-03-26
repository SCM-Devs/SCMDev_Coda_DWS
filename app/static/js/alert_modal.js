document.addEventListener('DOMContentLoaded', () => {
    const scrapBtn = document.querySelector("#scrap-btn")
    const alertModal = document.querySelector("#alert-message")

    const yesBtn = document.getElementById("yes-alert-btn")
    const noBtn = document.getElementById("no-alert-btn")



    scrapBtn.addEventListener('click', () => {
        alertModal.style.display = "flex"
    })

    yesBtn.addEventListener('click', async() => {

        console.log("scrappy")
        alertModal.style.display = "none"
        try {
            const response = await fetch("http://localhost:5000/scrap-run")
            const data = await response.json()
            console.log(data.message)
            console.log(data.output)
        } catch (error) {
            console.error("Erreur lors de l'exécution", error)
        }

    })

    noBtn.addEventListener('click', () => {
        alertModal.style.display = "none"
    })
})