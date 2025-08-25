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
        image1 = request.files['image1']
        image2 = request.files['image2']
        image1.save('public/images/1.jpg')
        image2.save('public/images/2.jpg')

        finetune_inst = request.form.get('finetune', '')
        do_init = request.form.get('do_init', True)

        if do_init == 'true':
            init()
        
        result = main(finetune_inst)

        return send_file(f'public/images/3_{result['id']}.png',
            mimetype='image/png', as_attachment=False)
    except Exception as e:
        print(f"E:{e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
    #port = int(os.environ.get('PORT', 5000))
    #app.run(host='0.0.0.0', port=port)