# Projet DWS - Scraping et Affichage de Produits

## Description

Ce projet permet de récupérer des données produits à partir d'un fichier CSV et de les afficher sur une page web. Le backend est développé avec **Flask** et le frontend permet d'afficher les produits sous forme de cartes avec pagination. Il inclut aussi un système de recherche par nom de produit. L'application sert à manipuler des données de produits, les afficher dynamiquement, et inclure des fonctionnalités telles que la recherche et la pagination.

## Fonctionnalités

- **Pagination** : Affichage des produits avec pagination pour éviter de charger toutes les données d'un coup.
- **Recherche** : Système de recherche permettant de filtrer les produits par nom.
- **Vue détaillée des produits** : En cliquant sur un produit, une page détaillée s'affiche avec plus d'informations.
- **Backend Flask** : Serveur Flask pour gérer les API et le rendu des pages HTML.

## Prérequis

Avant de commencer, vous devez vous assurer que **Python** est installé sur votre machine.

### Installer Python

Si vous n'avez pas Python, vous pouvez le télécharger depuis le site officiel : [https://www.python.org/downloads/](https://www.python.org/downloads/)

### Installer un environnement virtuel

Créez un environnement virtuel pour isoler les dépendances du projet.

python -m venv venv

### Activer l'environnement virtuel

    Sur Windows :
venv\Scripts\activate

Sur Mac/Linux :
source venv/bin/activate

### Installer les dépendances

pip install -r requirements.txt

### Lancer l'application

Une fois les dépendances installées, vous pouvez lancer le serveur Flask avec la commande suivante :

python run.py

Le serveur sera lancé sur http://127.0.0.1:5000 par défaut, uen autre ligne sera visible dans la console pour indiquer l'adresse exacte sur laquelle les appareils connectés au même réseau pourront avoir accès.
Cette ligne commence comme ça : 
"Application accessible sur : "


PS: le script de scraping dure uen dizaine de minutes, il est donc préférable de le lancer avant de lancer le serveur Flask, voici la ligne a tapé:
python scrappy.py

PSS: toutes les dépendances ne sont peut-être pas incluses dans le projet, il faudra peut-être en installer d'autres
