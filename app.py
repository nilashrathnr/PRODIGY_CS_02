from flask import Flask, request, jsonify, send_from_directory
import numpy as np
import cv2
import base64
from io import BytesIO
from PIL import Image
import random, os


app = Flask(__name__)

# Your existing routes

@app.route('/static/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Helper function to convert base64 to an image
def base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str.split(',')[1])
    img = Image.open(BytesIO(image_data))
    return np.array(img)

# Helper function to convert image to base64
def image_to_base64(image):
    img = Image.fromarray(image.astype('uint8'))
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode()

@app.route('/encrypt', methods=['POST'])
def encrypt_image():
    data = request.json
    image_base64 = data['image']
    
    # Convert base64 to image
    image = base64_to_image(image_base64)
    
    # Convert to grayscale and apply encryption (simple pixel manipulation)
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    key = np.random.rand(*grayscale_image.shape)
    encrypted_image = np.clip(grayscale_image / (key + 0.001), 0, 255)
    
    # Convert back to base64
    encrypted_image_base64 = image_to_base64(encrypted_image)
    
    return jsonify({'encrypted_image': encrypted_image_base64})

@app.route('/decrypt', methods=['POST'])
def decrypt_image():
    data = request.json
    image_base64 = data['image']
    
    # Convert base64 to image
    encrypted_image = base64_to_image(image_base64)
    
    # Decrypt the image (reverse operation)
    key = np.random.rand(*encrypted_image.shape)
    decrypted_image = np.clip(encrypted_image * (key + 0.001), 0, 255)
    
    # Convert back to base64
    decrypted_image_base64 = image_to_base64(decrypted_image)
    
    return jsonify({'decrypted_image': decrypted_image_base64})

if __name__ == "__main__":
    app.run(debug=True)
