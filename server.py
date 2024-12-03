import os
import json
import requests
from flask import Flask, Response
from collections import OrderedDict

class LFUCache:
    def __init__(self, capacity_bytes=5 * 1024 * 1024, cache_dir='cache'):
        self.capacity_bytes = capacity_bytes
        self.current_size = 0
        self.cache_dir = cache_dir
        self.frequency_file = os.path.join(cache_dir, 'frequency.json')
        self.cache = OrderedDict()
        self.frequency = {}

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        if os.path.exists(self.frequency_file):
            with open(self.frequency_file, 'r') as f:
                self.frequency = json.load(f)

        for filename in os.listdir(cache_dir):
            if filename != 'frequency.json':
                file_path = os.path.join(cache_dir, filename)
                self.cache[filename] = file_path
                self.current_size += os.path.getsize(file_path)

    def save_frequency(self):
        with open(self.frequency_file, 'w') as f:
            json.dump(self.frequency, f)

    def get(self, key):
        if key not in self.cache:
            return None

        self.frequency[key] += 1
        self.save_frequency()
        
        file_path = self.cache[key]
        with open(file_path, 'rb') as f:
            data = f.read()

        value = self.cache.pop(key)
        self.cache[key] = value
        return data

    def put(self, key, value):
        file_size = len(value)
        if key in self.cache:
            self.frequency[key] += 1
            self.save_frequency()
            return

        while self.current_size + file_size > self.capacity_bytes:
            lfu_key = min(self.frequency, key=self.frequency.get)
            lfu_file_path = self.cache[lfu_key]
            self.current_size -= os.path.getsize(lfu_file_path)
            os.remove(lfu_file_path)
            del self.cache[lfu_key]
            del self.frequency[lfu_key]

        file_path = os.path.join(self.cache_dir, key)
        with open(file_path, 'wb') as f:
            f.write(value)

        self.cache[key] = file_path
        self.frequency[key] = 1
        self.current_size += file_size
        self.save_frequency()

app = Flask(__name__)
ORIGIN_SERVER = 'http://localhost:8000' 

image_cache = LFUCache(capacity_bytes=10 * 1024 * 1024)  

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
