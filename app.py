from flask import Flask, request, jsonify
import face_recognition
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

known_faces = []

@app.route('/')
def index():
    return 'Face Recognition API Aktif!'

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "File gambar tidak ditemukan"})

    file = request.files['image']
    name = request.form.get('name', 'unknown')
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    image = face_recognition.load_image_file(path)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        return jsonify({"status": "error", "message": "Wajah tidak terdeteksi"})

    known_faces.append({
        "name": name,
        "encoding": encodings[0]
    })

    return jsonify({"status": "success", "message": f"Wajah {name} ditambahkan"})

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'image' not in request.files:
        return jsonify({"status": "error", "message": "File gambar tidak ditemukan"})

    file = request.files['image']
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)

    if not encodings:
        return jsonify({"status": "error", "message": "Wajah tidak terdeteksi"})

    unknown_face = encodings[0]
    for face in known_faces:
        result = face_recognition.compare_faces([face['encoding']], unknown_face)
        if result[0]:
            return jsonify({"match": True, "name": face['name']})

    return jsonify({"match": False, "message": "Tidak ada kecocokan"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
