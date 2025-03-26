document.addEventListener('DOMContentLoaded', () => {
    const scrapBtn = document.querySelector("#scrap-btn")
    const alertModal = document.querySelector("#alert-message")

    const yesBtn = document.getElementById("yes-alert-btn")
    const noBtn = document.getElementById("no-alert-btn")

    scrapBtn.addEventListener('click', () => {
        alertModal.style.display = "flex"
    })

    yesBtn.addEventListener('click', () => {
                //Lancer le bot de scrap ici

                console.log("scrappy")
        alertModal.style.display = "none"

    })

    noBtn.addEventListener('click', () => {
        alertModal.style.display = "none"
    })
})