import os
import cv2
import CNN_test
import numpy as np
from flask import Flask, request, render_template, flash, url_for, redirect

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)

@app.route('/res', methods=['GET','POST'])

def result(solution):
    return render_template('result.html', res=solution)

@app.route('/', methods=['GET', 'POST'])

def upload_file():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        
        file = request.files['file1']

        if allowed_file(file.filename):
            file_bytes = np.fromfile(file, np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
            res = CNN_test.predict(img)
            if len(res) != 0:
                return render_template('result.html', res=res)
        else:
            flash("Please upload an image in png, jpg or jpeg format.")

    return render_template("index.html")

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)