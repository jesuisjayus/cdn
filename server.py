from flask import Flask, send_from_directory, abort, Response
import os
import requests

app = Flask(__name__)

IMAGE_FOLDER = '.'

SERVERS = ['http://localhost:8000']  

@app.route('/<image_name>', methods=['GET'])
def get_image(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)

    # Vérifie si l'image existe localement
    if os.path.exists(image_path) and os.path.isfile(image_path):
        return send_from_directory(IMAGE_FOLDER, image_name)

    # Si l'image n'est pas trouvée localement -> interroge les autres serveurs
    for server in SERVERS:
        try:
            response = requests.get(f'{server}/{image_name}', timeout=5)
            if response.status_code == 200: # Image trouvée
                return Response(response.content, content_type=response.headers['Content-Type'])
        except requests.RequestException:
            continue

    # Si l'image n'a pas été trouvée sur ce serveur ni sur les autres, renvoyer une image par défaut
    return send_from_directory(IMAGE_FOLDER, 'default.webp')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
