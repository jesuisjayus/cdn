from flask import Flask, send_from_directory
import os

app = Flask(__name__)

IMAGE_FOLDER = '.'

@app.route('/<image_name>', methods=['GET'])
def get_image(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)

    # Vérifie si l'image existe sur ce serveur
    if os.path.exists(image_path) and os.path.isfile(image_path):
        return send_from_directory(IMAGE_FOLDER, image_name)
    else:
        return send_from_directory(IMAGE_FOLDER, 'default.webp')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
