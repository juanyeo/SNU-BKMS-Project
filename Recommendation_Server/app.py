import os
import torch
import torch.nn as nn
import yaml
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for
import googletrans
from mips_ALSH import Mips, HashFt, Hash_Table

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
    
# ----------------- ML part ----------------------
# Load google translator
translator = googletrans.Translator()

# Load model
model = torch.load('model.pth')
model.eval()
print("ML part loading complete\n")

# --------------- Data Loading part -----------------
df = pd.read_csv('SOF_dbms.csv')
title = [text for text in df['title']]
body = [text for text in df['body']]

title_embedding = model.encode(title, convert_to_tensor=True)
body_embedding = model.encode(body, convert_to_tensor=True)
hashft_class = HashFt(params)
hashft = hashft_class.hash_functions
title_hash_table = Hash_Table(params, hashft, title_embedding)
title_Data = title_hash_table.table
body_hash_table = Hash_Table(params, hashft, body_embedding)
body_Data = body_hash_table.table

search_engine = Mips(hashft, params)
print("Search Engine Loading complete\n")
# ----------------- Flask part ----------------------
app = Flask(__name__)

@app.route('/')
def Question():
    
    return render_template('Question.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'GET':

        question = request.args["question_title"]
        question = translator.translate(question, dest = 'en').text
        ranking = search_engine.search(model.encode([question], convert_to_tensor=True), title_Data, body_Data)
        ranking_dict = {'www.stackoverflow.com/questions/' + str(df.iloc[int(ranking[-i]), 1]): df.iloc[int(ranking[-i]), 2] for i in range(len(ranking))}
        
        return jsonify(ranking_dict)



if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
    
    """
    시나리오. 데모영상의 구체적인 시나리오.
    cherry pick을 보여주기. 어떤 데이터가 가장 이쁜가.
    
    
    데이터 가져오는 플라스크 서버 
    
    output을 json 형식으로 보내기
    
    """
    
