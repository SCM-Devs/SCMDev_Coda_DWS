# from app import create_app

# app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True)

from app import create_app
import socket

app = create_app()

if __name__ == '__main__':
    # Récupérer automatiquement l'adresse IP locale
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"Application accessible sur : http://{ip_address}:5000")

    # Lancer l'application Flask sur toutes les interfaces réseau pour qu'elle soit accessible
    app.run(host='0.0.0.0', port=5000, debug=True)
