from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
@app.route('/upload/<folder>', methods=['POST'])
def upload_image(folder):
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Tạo thư mục nếu chưa có
    save_dir = os.path.join("Undatabase", folder)
    os.makedirs(save_dir, exist_ok=True)

    # Lưu file với đường dẫn đầy đủ
    file_path = os.path.join(save_dir, file.filename)
    file.save(file_path)

    return jsonify({'message': 'File uploaded successfully!'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)