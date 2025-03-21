# E-Commerce API Documentation

## Overview
This is a Flask-based e-commerce API that allows users to:
- Upload and categorize products using AI (MobileNetV2)
- Fetch product lists with optional filtering by sentiment
- Add and analyze product reviews using Hugging Face sentiment analysis

## Setup Instructions
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo.git
   cd your-repo
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```sh
   HUGGING_FACE_API_KEY=your_huggingface_api_key
   ```
4. Run the server:
   ```sh
   python app.py
   ```

## API Endpoints

### **1. Get Product Image**
**Endpoint:** `GET /uploads/<filename>`
- Returns the requested product image.

### **2. Add Product**
**Endpoint:** `POST /products`
- **Description:** Upload a new product with an image. The image is analyzed to determine the product category.
- **Request Body (multipart/form-data):**
  | Field  | Type   | Description         |
  |--------|--------|---------------------|
  | name   | string | Name of the product |
  | price  | float  | Price of the product |
  | image  | file   | Image of the product |
- **Response:**
  ```json
  {
    "message": "Product added",
    "data": {
      "id": "uuid",
      "name": "Product Name",
      "category": "Predicted Category",
      "price": 100.0,
      "image_url": "/uploads/filename.jpg",
      "created_at": "timestamp"
    }
  }
  ```

### **3. Get Product List**
**Endpoint:** `GET /products`
- **Query Parameters (optional):**
  | Parameter | Type   | Description                     |
  |----------|--------|---------------------------------|
  | emotion  | string | Filter by sentiment (POSITIVE) |
- **Response:**
  ```json
  {
    "data": [
      {
        "id": "uuid",
        "name": "Product Name",
        "category": "Category",
        "price": 100.0,
        "image_url": "/uploads/filename.jpg",
        "created_at": "timestamp",
        "emotion": "POSITIVE"
      }
    ]
  }
  ```

### **4. Add Product Review**
**Endpoint:** `POST /reviews`
- **Description:** Adds a review and performs sentiment analysis.
- **Request Body (JSON):**
  ```json
  {
    "productId": "uuid",
    "comment": "This product is amazing!"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Review added",
    "data": {
      "id": "uuid",
      "productId": "uuid",
      "comment": "This product is amazing!",
      "emotion": "POSITIVE",
      "score": 0.99,
      "createdAt": "timestamp"
    }
  }
  ```

## Notes
- The image classification uses `MobileNetV2`.
- Sentiment analysis is done via Hugging Face API.
- Ensure the `.env` file contains a valid Hugging Face API key.

## License
This project is licensed under the MIT License.

