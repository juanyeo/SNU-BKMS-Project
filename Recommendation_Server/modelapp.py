import os
import torch
import torch.nn as nn
import yaml
from flask import Flask, render_template, request, jsonify, redirect, url_for
import googletrans
from mips_ALSH import Mips, HashFt

config_path = 'config.yaml'
hashft_path = 'gen_ids/hash_ft.pickle'

# ----------------- Load parameters-----------------

if config_path in os.listdir():
    with open(config_path, 'r') as f:
        params = yaml.load(f, Loader = yaml.FullLoader)
else:
    raise f"{config_path} does not exists"

if hashft_path in os.listdir():
    with open(hashft_path, 'r') as f:
        params = yaml.load(f, Loader = yaml.FullLoader)
else:
    print(f"hashft_path: {hashft_path} does not exists. Create new hash function\n")

print("Completed Load Parameters")    
# ----------------- ML part ----------------------
translator = googletrans.Translator()
# Load hash functions
hash_fts = HashFt(params, None)
# Load search engine
search_engine = Mips(hash_fts, params)
# Load model
model = torch.load('model.pth')
model.eval()

print("Complete Load ML models")
# ----------------- Flask part ----------------------
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        sentence = request.form['sentence']
        # redirect to another page and pass the sentence as a URL parameter
        return redirect(url_for('predict', sentence=sentence))
    return render_template('home.html')

@app.route('/stackoverflow/predict', methods=['GET'])
def so_predict():
    sentence = request.args.get('sentence')
    # use the sentence in your model
    embedding = model.encode([sentence])
    ranking = search_engine.search(embedding, None)
    
    return render_template('predict.html', sentence=sentence, ranking=ranking)

@app.route('/etl/predict', methods=['GET'])
def etl_predict():
    sentence = request.args.get('sentence')
    # use the sentence in your model
    embedding = model.encode([sentence])
    ranking = search_engine.search(embedding, None)
    
    return render_template('predict.html', sentence=sentence, ranking=ranking)

if __name__ == '__main__':
    app.run(debug=True)