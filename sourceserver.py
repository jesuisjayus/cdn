import os
from flask import Flask, send_from_directory
from werkzeug.middleware.shared_data import SharedDataMiddleware

app = Flask(__name__)
IMAGE_FOLDER = './images'  
os.makedirs(IMAGE_FOLDER, exist_ok=True)

@app.route('/<image_name>', methods=['GET'])
def get_image(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    
    if os.path.exists(image_path) and os.path.isfile(image_path):
        return send_from_directory(IMAGE_FOLDER, image_name)
    
    return 'Image not found', 404

if __name__ == '__main__':
    app.run(host='3.3.3.3', port=8000)