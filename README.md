# Projet DWS - Scraping et Affichage de Produits

## 📍 Le Principe ?

Ce projet permet de récupérer des données produits à partir du site Extime.com, de les sauvegarder dans un fichier CSV, et de les afficher sur une page web.

Le backend est développé avec Flask, et le frontend permet d'afficher les produits sous forme de cartes avec pagination. Il inclut également un système de recherche par nom de produit.

L'application a pour objectif de manipuler et afficher dynamiquement des données de produits, en offrant des fonctionnalités essentielles telles que la recherche, la modification et la pagination. Nous avons porté une attention particulière à l'expérience utilisateur en optimisant l'affichage et la navigation.

## 👉 Sur l'application, vous pouvez :
- **Rechercher** : Système de recherche par nom de produit, géré en JavaScript et via le framework Flask, permettant la liaison entre le front-end et le back-end.
- **Voir les détails d'un produit** : En cliquant sur un produit, une page dédiée affiche plus d'informations. Cette page est distincte de celle de la recherche, avec des fichiers séparés.
- **Modifier un produit** : Depuis sa fiche, vous pouvez modifier les informations et enregistrer les changements. La sauvegarde met directement à jour le fichier CSV utilisé par l'application.
- **Naviguer avec pagination** : La liste des produits est paginée pour éviter de charger toutes les données d’un coup. La pagination est également disponible dans les résultats de recherche.
- **Lancer le Scraping** : Un bouton intégré à l'application permet de démarrer le scraping. À noter que le processus peut prendre environ 30 minutes, notamment à cause du téléchargement des images. Profitez-en pour faire une pause ! 😉

ℹ️ Attention : Lisez attentivement les étapes d’installation, notamment concernant le scraping. Pour plus de détails sur son fonctionnement, rendez-vous dans la section "Explication Scraping" ci-dessous.

## 🔧 Installation

Avant de commencer, vous devez vous assurer que **Python** est installé sur votre machine.

### Installer Python
Si vous n'avez pas Python, vous pouvez le télécharger depuis le site officiel : [https://www.python.org/downloads/](https://www.python.org/downloads/)


### Installer un environnement virtuel
Créez un environnement virtuel pour isoler les dépendances du projet : `python -m venv venv`


### Activer l'environnement virtuel
Sur Windows :
`venv\Scripts\activate`

Sur Mac/Linux :
`source venv/bin/activate`

### Installer les dépendances
 Toujours dans votre terminal, entrer : `pip install -r requirements.txt`

### Lancer l'application
Une fois les dépendances installées, vous pouvez lancer le serveur Flask avec la commande suivante : 

Sur Windows :
`python run.py`

Sur Mac/Linux :
`python3 mon_script.py`

Le serveur sera lancé sur http://127.0.0.1:5000 par défaut ( vous pouvez ouvrir l'application sur le navigateur de votre choix ). Une autre ligne sera visible dans la console pour indiquer l'adresse exacte sur laquelle les appareils connectés au même réseau pourront avoir accès.
Cette ligne commence comme ça : "Application accessible sur : "

### Une fois sur l'application
Avant de lancer l’application, vous devez impérativement exécuter un premier scraping pour créer le fichier CSV contenant les produits.

Nous recommandons de le lancer avant le serveur Flask :
`python extime_scraper/main.py`

## 🧠 Notre Réflexion

### **Recherche par EAN**
Pour ce projet, une recherche par EAN en complément de la recherche par nom aurait été intéressante. Cependant, nous avons rapidement constaté que cette fonctionnalité posait des défis. En effet, il aurait fallu disposer de tous les codes EAN des produits scrapés pour les comparer au CSV. Pour y parvenir, plusieurs options s'offraient à nous :

1. Utiliser une API externe fournissant les codes EAN. Cependant, ces API sont souvent payantes au-delà d’un certain nombre de requêtes, ce qui ne correspondait pas à notre besoin. (La liste des API envisagées est détaillée ci-dessous.)
2. Obtenir les données directement du client. Cependant, ces informations étant sensibles, cette solution n’a pas été retenue.

📍 **Liste des API envisagées pour la recherche EAN**
1. EAN-Search.org
Accès à plus de 890 millions de codes-barres
Réponses en XML et JSON
Compatible avec Java, PHP, Python...
Inconvénient : Abonnement payant pour un accès complet

2. Barcode Lookup API
Fournit des détails produits (description, images, prix...
Facile à utiliser
Inconvénient : Système de crédits limitant l'accès

3. GTIN API (Product-Search.net)
Recherche par GTIN, EAN, UPC, ISBN
Réponses en JSON et XML
Inconvénient : Base de données non exhaustive

4. Base de données de codes-barres (data.gouv.fr)
Gratuit et open source
Inconvénients : Mise à jour irrégulière, données parfois incomplètes

5. UPCitemdb
Recherche rapide dans une base de données UPC/EAN
Inconvénients : Restrictions sur les requêtes gratuites, version premium coûteuse

6. Google Shopping API
Recherche avancée sur prix et produits
Inconvénient : API payante et complexe à implémenter

7. Open Beauty Facts API
Base de données spécialisée sur les cosmétiques
Inconvénient : Fiabilité variable selon les contributions

8. Open Products Facts API
Informations sur divers produits
Inconvénient : Encore en développement, certaines catégories manquantes

9. ISBNdb API
Spécialisée dans les livres avec une base de données complète
Inconvénient : Version avancée payante

## 📑Explication Scraping

Lorsque vous lancez le scraping, le programme recherche sur le site toutes les informations nécessaires et extrait les données des produits dans chaque page des catégories sélectionnées.

Pour chaque produit, il :
- ✅ Télécharge l’image et la convertit en WebP (si elle n’existe pas déjà).
- ✅ Vérifie et élimine les doublons, en ne conservant que l’essentiel.
- ✅ Génère un fichier CSV contenant toutes les informations dans le dossier app/output.  

⏳ Durée d’exécution : environ 30 minutes sur Windows, légèrement plus rapide sur Mac.

Malgré nos efforts, notre bot de scraping ne récupère pas toutes les données correctement. Certains produits peuvent être absents, et certaines informations peuvent être incomplètes ou erronées.
Nous avons identifié ces limitations, mais en raison des contraintes de temps, nous n'avons pas pu les corriger entièrement avant la remise du projet.
Ce README vise à être transparent sur l’état actuel du projet et notre volonté de réussir. 

## 🆕 Évolutions possibles
Notre projet a bien avancé et propose déjà une base fonctionnelle, mais il reste encore plusieurs points à affiner et des fonctionnalités à développer pour atteindre tout son potentiel. Ce projet scolaire nous a permis de poser des bases solides, et nous voyons maintenant clairement les prochaines étapes pour l’améliorer.

1. Améliorations
- **Optimisation du Scraping** : Actuellement fonctionnel, il pourrait être accéléré et fiabilisé pour mieux gérer les volumes de données.
- **Sauvegarde des modifications** : L'enregistrement des modifications fonctionne, mais il pourrait être optimisé pour être plus efficace et sécurisé.

2. Nouvelles fonctionnalités à implémenter
- **Recherche par EAN** : Une fonctionnalité clé qui apporterait une vraie valeur ajoutée. Il serait intéressant de discuter avec le client pour identifier la meilleure approche technique.
- **Filtres avancés** : L'interface des filtres (bouton et menu déroulant) est déjà présente, mais leur fonctionnalité n’a pas encore été développée côté back-end. Une implémentation permettrait d’améliorer l’expérience utilisateur en affinant les résultats de recherche.
- **Navigation fluide entre les produits** : Ajouter des flèches de navigation sur les fiches produit pour passer d’un produit à l’autre sans revenir à la recherche. Les éléments visuels existent déjà, mais le système doit encore être connecté aux données.

Ces améliorations sont autant d’opportunités pour renforcer la performance et l’ergonomie de l’application. Avec du temps et des itérations, ce projet pourrait aboutir à un outil complet et optimisé. 🔥

## 📢 Remarque finale
Ceci est le repositiry final que nous utilisons pour livrer le projet. Mais nous avons travailler sur un repository parallèle afin de livrer une version propre. Nous vous mettons tout de même le lien du repository de travaille pour témoigner de nos effort au cours des trois dernière semaine. 
👉 https://github.com/SCM-Devs/SCMDev_Coda_DWS

Ce projet a été réalisé dans un cadre scolaire. Malgré les imperfections, il démontre notre capacité à concevoir un bot de scraping, à exploiter les données récupérées et à les présenter sous forme d’application web.

Merci de votre compréhension et bonne utilisation ! 🚀
