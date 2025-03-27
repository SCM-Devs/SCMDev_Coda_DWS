document.addEventListener('DOMContentLoaded', function(){
    const dropdownBtn = document.querySelector("#dropdown-btn")
    const dropdownMenu = document.querySelector("#dropdown-menu")


    dropdownBtn.addEventListener("click", function() {
        dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block"
    })

    dropdownMenu.addEventListener("click", function(event) {
        if (event.target.tagName === "LI") {
            if (dropdownMenu.dataset.value === "material"){
                dropdownBtn.textContent = "Matériau : " + event.target.dataset.value

            } else if (dropdownMenu.dataset.value === "category") {
                document.querySelectorAll("li").forEach(li => li.style.background = "transparent")
                event.target.style.background = "#dadada"
            }
            
            dropdownMenu.style.display = "none"
        }
    })

    document.addEventListener("click", function(event) {
        if (!dropdownBtn.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.style.display = "none"
        }
    })
})
