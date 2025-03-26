export default class Product {
    constructor(data) {
        this.name = data.name
        this.brand = data.brand
        this.volume = data.volume
        this.categorie = data.categorie


    }

    render() {
        return `
            <div class="productCard">
                <a href="/${this.name}" class="Card">

                    <div class="futureImg"> 
                        <img src="../static/images/image.webp" alt="Description de l'image">
                    </div>
                    <div class="fastInformations">
                        <p>Nom : ${this.name}</p>
                        <p>Marque : ${this.brand}</p>
                        <p>Volume : ${this.volume}</p>
                        <p>Catégorie : ${this.categorie}</p>
                    </div>
                </a>
            </div>
        `
    }
}
