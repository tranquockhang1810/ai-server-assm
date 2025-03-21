from collections import Counter
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import tensorflow as tf
import numpy as np
from PIL import Image
from dotenv import load_dotenv
import os
import uuid
import datetime
load_dotenv() 

app = Flask(__name__)
CORS(app)

# Hugging Face API
HUGGING_FACE_ANALYZE_API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"
HEADERS = {"Authorization": "Bearer " + os.getenv("HUGGING_FACE_API_KEY")}

# Thư mục lưu ảnh
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model AI phân loại sản phẩm
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Danh sách lưu trữ sản phẩm và đánh giá
products = [
  {
      "category": "jersey",
      "created_at": "2025-03-21T07:14:29.104050",
      "id": "0d02fa10-ebf5-4ed5-9d46-0dac412fe246",
      "image_url": "/uploads/415a5510-784d-4815-ad47-555906011767.jpg",
      "name": "Purple Jersey",
      "price": 100000.0
  },
  {
      "category": "suit",
      "created_at": "2025-03-21T07:14:54.773084",
      "id": "ec0ceb36-9bba-4bbc-83a9-e0aabbfb8ace",
      "image_url": "/uploads/4302363b-0624-466a-a124-f96a662774e3.jpg",
      "name": "Trousers",
      "price": 100000.0
  }
]

reviews = [
  {
    "comment": "It's bad",
    "createdAt": "2025-03-21T07:51:34.064346",
    "emotion": "NEGATIVE",
    "id": "f4792266-df59-464e-aef4-1508139cd262",
    "productId": "ec0ceb36-9bba-4bbc-83a9-e0aabbfb8ace",
    "score": 0.999804675579071
  },
  {
    "comment": "Very nice shirt",
    "createdAt": "2025-03-21T07:53:16.385696",
    "emotion": "POSITIVE",
    "id": "fcd3927e-d8d2-498c-b3ab-7b1e5bbd15c8",
    "productId": "0d02fa10-ebf5-4ed5-9d46-0dac412fe246",
    "score": 0.99986732006073
  }
]

# API lấy ảnh từ thư mục
@app.route('/uploads/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# API thêm sản phẩm
@app.route('/products', methods=['POST'])
def add_product():
  try:
    data = request.form
    file = request.files['image']

    # Lưu ảnh vào thư mục
    filename = str(uuid.uuid4()) + ".jpg"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(image_path)

    # Xử lý ảnh cho model AI
    image = Image.open(image_path).resize((224, 224)).convert('RGB')
    image_array = np.array(image) / 255.0
    image_array = np.expand_dims(image_array, axis=0)

    # AI phân loại
    predictions = model.predict(image_array)
    category = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0][0][1]

    # Lưu vào danh sách sản phẩm
    new_product = {
        'id': str(uuid.uuid4()),
        'name': data['name'],
        'category': category,
        'price': float(data['price']),
        'image_url': f"/uploads/{filename}",
        'created_at': datetime.datetime.utcnow().isoformat()
    }
    products.append(new_product)

    return jsonify({'message': 'Product added', 'data': new_product}), 201
  except Exception as e:
    return jsonify({'error': str(e)})

# API lấy danh sách sản phẩm
@app.route('/products', methods=['GET'])
def get_products():
    emotion_filter = request.args.get('emotion')

    result = []
    for product in products:
        product_reviews = [review for review in reviews if review['productId'] == product['id']]
        
        emotions = [review['emotion'] for review in product_reviews]

        most_common_emotion = Counter(emotions).most_common(1)
        dominant_emotion = most_common_emotion[0][0] if most_common_emotion else "No reviews"

        if emotion_filter and dominant_emotion.lower() != emotion_filter.lower():
            continue
        
        result.append({
            'id': product['id'],
            'name': product['name'],
            'category': product['category'],
            'price': product['price'],
            'image_url': product['image_url'],
            'created_at': product['created_at'],
            'emotion': dominant_emotion
        })

    return jsonify({ "data": result}), 200

# API đánh giá sản phẩm + AI phân tích cảm xúc
@app.route('/reviews', methods=['POST'])
def add_review():
  try:
    data = request.json

    # AI phân tích cảm xúc
    response = requests.post(HUGGING_FACE_ANALYZE_API_URL, headers=HEADERS, json={"inputs": data['comment']})
    emotion = response.json()[0][0]['label']
    score = response.json()[0][0]['score']

    new_review = {
        'id': str(uuid.uuid4()),
        'productId': data['productId'],
        'comment': data['comment'],
        'emotion': emotion,
        'score': score,
        'createdAt': datetime.datetime.utcnow().isoformat()
    }
    reviews.append(new_review)

    return jsonify({'message': 'Review added', 'data': new_review}), 201
  except Exception as e:
    return jsonify({'error': str(e)})

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=5000)
