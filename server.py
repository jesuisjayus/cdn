import requests
from flask import Flask, Response
from collections import OrderedDict

class LFUCache:
    def __init__(self, capacity=3):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.frequency = {}

    def get(self, key):
        if key not in self.cache:
            return None

        self.frequency[key] += 1
        
        value = self.cache[key]
        del self.cache[key]
        self.cache[key] = value
        return value

    def put(self, key, value):
        if key in self.cache:
            self.cache[key] = value
            self.frequency[key] += 1
            return

        if len(self.cache) >= self.capacity:
            lfu_key = min(self.frequency, key=self.frequency.get)
            del self.cache[lfu_key]
            del self.frequency[lfu_key]

        self.cache[key] = value
        self.frequency[key] = 1

app = Flask(__name__)
ORIGIN_SERVER = 'http://localhost:8000' 

image_cache = LFUCache(capacity=3)

@app.route('/<image_name>', methods=['GET'])
def get_image(image_name):
    cached_image = image_cache.get(image_name)
    if cached_image:
        return Response(cached_image, mimetype='image/jpg')
    try:
        response = requests.get(f'{ORIGIN_SERVER}/{image_name}', timeout=5)
        if response.status_code == 200:
            image_cache.put(image_name, response.content)
            return Response(response.content, mimetype=response.headers.get('Content-Type', 'image/webp'))
    except requests.RequestException:
        pass

    return 'Image not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)