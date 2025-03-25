document.addEventListener('DOMContentLoaded', () => {
    const scrapBtn = document.querySelector("#scrap-btn")
    const overlay = document.querySelector("#overlay")
    const alertModal = document.querySelector("#alert-message")

    const yesBtn = document.getElementById("yes-alert-btn")
    const noBtn = document.getElementById("no-alert-btn")

    scrapBtn.addEventListener('click', () => {
        alertModal.style.display = "flex"
        overlay.style.display = "flex"
    })

    yesBtn.addEventListener('click', () => {
        //Lancer le bot de scrap ici
        
        alertModal.style.display = "none"
        overlay.style.display = "none"
    })

    noBtn.addEventListener('click', () => {
        alertModal.style.display = "none"
        overlay.style.display = "none"
    })
})