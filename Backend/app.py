from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import cv2
import numpy as np
import face_recognition
import os
import base64
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRAINING_IMAGES_DIR = os.path.join(BASE_DIR, 'Training_images')
HOSTEL_LOG_FILE = os.path.join(BASE_DIR, 'HostelEntryExit.csv')


def findEncodings(images):
    encodeList = []
    for img in images:
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(img)
            if faces:
                encode = face_recognition.face_encodings(img, faces)[0]
                encodeList.append(encode)
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            continue
    return encodeList


@app.route('/face_recognition', methods=['POST'])
def start_face_recognition():
    try:
        data = request.get_json()
        base64_image = data.get('image')

        if not base64_image:
            return jsonify({"message": "No image data provided"}), 400

        base64_image = re.sub('^data:image/.+;base64,', '', base64_image)
        image_data = base64.b64decode(base64_image)
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"message": "Image decoding failed"}), 400

        myList = os.listdir(TRAINING_IMAGES_DIR)
        images = []
        classNames = []

        for cl in myList:
            if cl.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(TRAINING_IMAGES_DIR, cl)
                curImg = cv2.imread(img_path)
                if curImg is not None:
                    images.append(curImg)
                    classNames.append(os.path.splitext(cl)[0])

        encodeListKnown = findEncodings(images)
        imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgS)

        if not facesCurFrame:
            return jsonify({"message": "No face detected"}), 400

        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
        best_match = None
        best_match_distance = float('inf')

        for encodeFace in encodesCurFrame:
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            if len(faceDis) > 0:
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex] and faceDis[matchIndex] < best_match_distance:
                    best_match = matchIndex
                    best_match_distance = faceDis[matchIndex]

        if best_match is not None:
            name = classNames[best_match].upper()
            status = markHostelEntryExit(name)

            return jsonify({
                "message": f"{status} marked",
                "name": name,
                "status": status,
                "confidence": float(1 - best_match_distance)
            })

        return jsonify({"message": "No matching face found"}), 400

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


def markHostelEntryExit(name):
    now = datetime.now()
    dtString = now.strftime('%H:%M:%S')
    dateString = now.strftime('%Y-%m-%d')
    status = "Entry"

    if not os.path.exists(HOSTEL_LOG_FILE):
        with open(HOSTEL_LOG_FILE, 'w') as f:
            f.write("Name,Date,Entry Time,Exit Time\n")

    lines = []
    with open(HOSTEL_LOG_FILE, 'r') as f:
        lines = f.readlines()

    # Check for latest unclosed entry
    updated = False
    for i in range(len(lines) - 1, 0, -1):  # Skip header and go in reverse
        entry = lines[i].strip().split(',')
        if len(entry) == 4 and entry[0] == name and entry[1] == dateString and entry[3] == '':
            lines[i] = f"{entry[0]},{entry[1]},{entry[2]},{dtString}\n"
            status = "Exit"
            updated = True
            break

    if not updated:
        lines.append(f"{name},{dateString},{dtString},\n")
        status = "Entry"

    with open(HOSTEL_LOG_FILE, 'w') as f:
        f.writelines(lines)

    return status



@app.route('/get_image')
def get_image():
    image_path = request.args.get('path')
    return send_file(image_path, mimetype='image/jpeg')


@app.route('/')
def home():
    return jsonify({"message": ""})


@app.route('/test-connection')
def test_connection():
    return jsonify({"status": "connected"})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
