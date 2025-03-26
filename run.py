from app import create_app  # Importation de la fonction create_app depuis le module app
import socket  # Importation du module socket pour obtenir l'adresse IP

app = create_app()  # Création de l'application Flask

if __name__ == '__main__':
    # Obtenir l'adresse IP de l'hôte
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"Application accessible sur : http://{ip_address}:5001")  # Affiche l'URL d'accès

    # Démarre l'application Flask
    app.run(host='0.0.0.0', port=5001, debug=True)