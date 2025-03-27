document.addEventListener('DOMContentLoaded', () => {
    const scrapBtn = document.querySelector("#scrap-btn")
    const alertModal = document.querySelector("#alert-message")
    const logOutput = document.querySelector("#log-output")
    const yesBtn = document.getElementById("yes-alert-btn")
    const noBtn = document.getElementById("no-alert-btn")

    scrapBtn.addEventListener('click', () => {
        alertModal.style.display = "flex"
    })

    yesBtn.addEventListener('click', async () => {
        logOutput.style.backgroundColor = 'white'
        logOutput.style.border = '2px solid green'
        logOutput.innerHTML = "<p>Lancement du scraping... veuillez attendre le prochain message avant de faire quoi que ce soit</p>"
        alertModal.style.display = "none"

        try {
            const response = await fetch("http://localhost:5000/scrap-run")
            const data = await response.json()

            if (response.ok) {
                logOutput.textContent = ''
                logOutput.innerHTML += `<p style="color: green;">✅ Scrapping terminé veuillez rechercher la page</p>`
                logOutput.style.backgroundColor = ' #d4d4d4'
                logOutput.style.border = '2px solid  #d4d4d4'


            } else {
                logOutput.textContent = ''
                logOutput.innerHTML += `<p style="color: red;">❌ ${data.error || "Erreur inconnue"}</p>`
            }

            if (data.output) {
                console.log("data output")
            }

            if (data.error) {
                logOutput.textContent = ''
                logOutput.innerHTML += `<pre style="color: red;">${data.error}</pre>`
                console.log("data error")
            }

        } catch (error) {
            console.error("Erreur lors de l'exécution", error)
            logOutput.innerHTML += `<p style="color: red;">❌ Erreur lors de l'exécution : ${error.message}</p>`
        }
    })

    noBtn.addEventListener('click', () => {
        alertModal.style.display = "none"
    })
})
