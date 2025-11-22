# app.py
from flask import Flask, request, jsonify, render_template
import os
import shutil
import uuid
import time
from headconn import Headconn

app = Flask(__name__, static_folder='public', static_url_path='')
sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    id_ = uuid.uuid4().hex[:8]
    hc = Headconn()
    hc.start()
    hc.imagine_prompt.append(prompt)
    hc.prompt_queue.put({"type": 'imagine', 'value': prompt})
    sessions[id_] = {'hc': hc, 'images': None, 'composite': None}
    return jsonify({'id': id_})

@app.route('/api/status/<id_>', methods=['GET'])
def status(id_):
    if id_ not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 404

    hc = sessions[id_]['hc']
    response = {'stage': 'processing'}

    if len(hc.state_record) > 1 and hc.state_record[-1].get('execution') == 'failed':
        response['stage'] = 'failed'
        return jsonify(response)

    if len(hc.images) == 2:
        if not sessions[id_]['images']:
            os.makedirs('public/images', exist_ok=True)
            img1_tmp = str(hc.work_dir / f'{hc.images[0]}.png')
            img2_tmp = str(hc.work_dir / f'{hc.images[1]}.png')
            img1_pub = f'images/{id_}_1.png'
            img2_pub = f'images/{id_}_2.png'
            shutil.copy(img1_tmp, 'public/' + img1_pub)
            shutil.copy(img2_tmp, 'public/' + img2_pub)
            sessions[id_]['images'] = [img1_pub, img2_pub]

        response['img1'] = sessions[id_]['images'][0]
        response['img2'] = sessions[id_]['images'][1]

    if len(hc.state_record) > 1 and hc.state_record[-1].get('agent') == 'compose' and hc.state_record[-1].get('execution') == 'success':
        if not sessions[id_]['composite']:
            comp_tmp = hc.compose_client.images[0]
            comp_pub = f'images/{id_}_3.png'
            shutil.copy(comp_tmp, 'public/' + comp_pub)
            sessions[id_]['composite'] = comp_pub

        response['composite'] = sessions[id_]['composite']
        response['stage'] = 'done'

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)