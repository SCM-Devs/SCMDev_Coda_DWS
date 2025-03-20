# from app import create_app

# app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True)

from app import create_app
import socket

app = create_app()

if __name__ == '__main__':
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"Application accessible sur : http://{ip_address}:5000")

    app.run(host='0.0.0.0', port=5000, debug=True)
