from flask import Flask, request, jsonify, render_template, send_file
from pathlib import Path
import os
from headconn import init, main

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_images():
    try:
        # Save uploaded images
        image1 = request.files['image1']
        image2 = request.files['image2']
        image1.save('public/images/1.jpg')
        image2.save('public/images/2.jpg')

        # # Get finetune instructions
        # finetune_inst = request.form.get('finetune', '')

        # # Initialize and process
        # init()
        # result = main(finetune_inst)
        # print(f"rrresult:{result}")

        return send_file(f'public/images/3_87750472.png', mimetype='image/png', as_attachment=False)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)