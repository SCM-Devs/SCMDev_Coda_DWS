document.addEventListener('DOMContentLoaded', function(){
    const dropdownBtn = document.querySelector("#dropdown-btn")
    const dropdownMenu = document.querySelector("#dropdown-menu")
    const materialValueInput = document.querySelector("#material-value")
    let materialValue = dropdownBtn.getAttribute("data-value")

    if (materialValue && materialValue.trim() !== "") {
        dropdownBtn.textContent = "Matériau : " + materialValue
    }

    dropdownBtn.addEventListener("click", function() {
        dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block"
    })

    dropdownMenu.addEventListener("click", function(event) {
        if (event.target.tagName === "LI") {
            if (dropdownMenu.dataset.value === "material"){
                const selectedValue = event.target.dataset.value

                dropdownBtn.textContent = "Matériau : " + selectedValue
                materialValueInput.value = selectedValue

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
