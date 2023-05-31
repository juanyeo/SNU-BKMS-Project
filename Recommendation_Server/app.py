import os
import torch
import torch.nn as nn
import yaml
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for
import googletrans
from mips_ALSH import Mips, HashFt, Hash_Table
from flask_cors import CORS, cross_origin

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

## hash functions
hashft_class = HashFt(params)
hashft = hashft_class.hash_functions

## stackoverflow data
StackOverflow_Data = pd.read_csv('SOF_dbms.csv')
SO_title = [text for text in StackOverflow_Data['title']]
SO_body = [text for text in StackOverflow_Data['body']]

SO_title_embedding = model.encode(SO_title, convert_to_tensor=True)
SO_body_embedding = model.encode(SO_body, convert_to_tensor=True)
SO_title_hash_table = Hash_Table(params, hashft, SO_title_embedding)
SO_title_Data = SO_title_hash_table.table
SO_body_hash_table = Hash_Table(params, hashft, SO_body_embedding)
SO_body_Data = SO_body_hash_table.table

print("Stack Overflow Data Loading complete")

## etl data
etl_Data = pd.read_csv('etl_Questions.csv')
etl_title = [text for text in etl_Data['title']]
etl_body = [text for text in etl_Data['content']]

etl_title_embedding = model.encode(etl_title, convert_to_tensor=True)
etl_body_embedding = model.encode(etl_body, convert_to_tensor=True)
etl_title_hash_table = Hash_Table(params, hashft, etl_title_embedding)
etl_title_Data = etl_title_hash_table.table
etl_body_hash_table = Hash_Table(params, hashft, etl_body_embedding)
etl_body_Data = etl_body_hash_table.table

print("ETL Data Loading complete")
search_engine = Mips(hashft, params)
print("Search Engine Loading Complete.\n")
# ----------------- Flask part ----------------------
app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def Question():
    
    return render_template('Question.html')

@app.route('/stackoverflow',methods = ['POST', 'GET']) ## stackoverflow data search engine.
@cross_origin()
def so_result():
    if request.method == 'GET':

        question = request.args["question_title"]
        question = translator.translate(question, dest = 'en').text
        SO_ranking = search_engine.search(model.encode([question], convert_to_tensor=True), SO_title_Data, SO_body_Data)
        ranking_dict = {'www.stackoverflow.com/questions/' + str(StackOverflow_Data.iloc[int(SO_ranking[-i-1]), 1]): StackOverflow_Data['title'][int(SO_ranking[-i-1])] for i in range(len(SO_ranking))}
        return jsonify(ranking_dict)

@app.route('/etl',methods = ['POST', 'GET']) ## ETL data search engine
@cross_origin()
def etl_result():
    if request.method == 'GET':

        question = request.args["question_title"]
        question = translator.translate(question, dest = 'en').text
        etl_ranking = search_engine.search(model.encode([question], convert_to_tensor=True), etl_title_Data, etl_body_Data)
        ranking_dict = {str(etl_Data['id'][int(etl_ranking[-i-1])]):etl_Data['title'][int(etl_ranking[-i-1])] for i in range(len(etl_ranking))} # Not Determined Yet.
        return jsonify(ranking_dict)


if __name__ == '__main__':
    app.run(debug=True)
    
    """
    시나리오. 데모영상의 구체적인 시나리오.
    cherry pick을 보여주기. 어떤 데이터가 가장 이쁜가.
    
    
    데이터 가져오는 플라스크 서버 
    
    output을 json 형식으로 보내기
    
    """
    
