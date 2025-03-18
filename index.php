<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Page</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/index.css"> <!-- Lien vers le fichier CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"> <!-- Lien vers Font Awesome -->
</head>
<body>
    <!-- Header -->
    <header>
        <h1>Scraping Extime</h1>
    </header>

    <!-- Search Section -->
    <section class="search-section">
        <div class="search-box">
            <div class="btn-group" role="group">
                <button type="button" class="btn active" id="name-btn">Nom</button>
                <button type="button" class="btn" id="ean-btn">EAN</button>
            </div>
            <input type="text" placeholder="Rechercher...">
            <button class="search-icon" type="button">
                <i class="fas fa-search"></i>
            </button>
        </div>
    </section>

    <script src="https://kit.fontawesome.com/a076d05399.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.11.6/dist/umd/popper.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.min.js"></script>
    <script src="assets/js/index.js"></script> <!-- Lien vers le fichier JavaScript -->
</body>
</html>