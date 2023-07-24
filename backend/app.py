# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/post-data', methods=['POST'])
def post_data():
    data = request.json  # Access the data sent in the request body as a JSON object
    # Process the 2D array data here (you can perform any necessary operations)
    # For this example, let's just return the received data
    
    return jsonify({"message": "Data received successfully!", "data": data})

if __name__ == '__main__':
    app.run(debug=True)
