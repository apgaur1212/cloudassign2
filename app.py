from flask import Flask, request, jsonify
import pyodbc
from azure.storage.blob import BlobServiceClient
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Azure SQL Database Configuration
DB_CONFIG = {
    "server": "product-server123.database.windows.net",
    "database": "productdb",
    "username": "apgaur1212",
    "password": "Aditya@123",
    "driver": "{ODBC Driver 18 for SQL Server}"
}

# Azure Blob Storage Configuration
BLOB_CONFIG = {
    "account_name": "assignstorage123",
    "account_key": "eyGn/+1ti79445BG2HqPv8k6UnKYIqd2oioYI7E/TUC2v5j7Oxx0JJMyWSw+B9LhJFc0tSkIKSGp+AStA9Uy7A==",
    "container_name": "product-images"
}

# Initialize Blob Service Client
blob_service_client = BlobServiceClient(account_url=f"https://{BLOB_CONFIG['account_name']}.blob.core.windows.net", credential=BLOB_CONFIG['account_key'])
container_client = blob_service_client.get_container_client(BLOB_CONFIG['container_name'])

# Function to connect to the database
def get_db_connection():
    try:
        conn = pyodbc.connect(
            f"DRIVER={DB_CONFIG['driver']};"
            f"SERVER={DB_CONFIG['server']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['username']};"
            f"PWD={DB_CONFIG['password']}"
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

# API to add a new product with optional image upload
@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.form
    file = request.files.get("image")
    required_fields = ["name", "description", "price", "category"]

    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    image_url = None
    if file:
        try:
            filename = secure_filename(file.filename)
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(file, overwrite=True)
            image_url = f"https://{BLOB_CONFIG['account_name']}.blob.core.windows.net/{BLOB_CONFIG['container_name']}/{filename}"
        except Exception as e:
            return jsonify({"error": f"Image upload failed: {str(e)}"}), 500

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Products (name, description, price, category, image_url) VALUES (?, ?, ?, ?, ?)",
            (data["name"], data["description"], data["price"], data["category"], image_url)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": "Product added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to get all products
@app.route('/products', methods=['GET'])
def list_products():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price, category, image_url FROM Products")

        products = [
            {
                "id": row[0], 
                "name": row[1], 
                "description": row[2], 
                "price": str(row[3]),  
                "category": row[4] if row[4] is not None else "Unknown",
                "image_url": row[5] if row[5] is not None else None
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return jsonify(products), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to search products by name or category
@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({"error": "Search query cannot be empty"}), 400

    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price, category, image_url FROM Products WHERE name LIKE ? OR category LIKE ?", 
                       ('%' + query + '%', '%' + query + '%'))

        products = [
            {
                "id": row[0], 
                "name": row[1], 
                "description": row[2], 
                "price": str(row[3]),  
                "category": row[4] if row[4] is not None else "Unknown",
                "image_url": row[5] if row[5] is not None else None
            }
            for row in cursor.fetchall()
        ]

        conn.close()
        return jsonify(products), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
