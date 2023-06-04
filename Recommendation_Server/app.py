import os
import random
import torch
import torch.nn as nn
import yaml
import pandas as pd
from flask import Flask, render_template, request, jsonify, redirect, url_for
import googletrans
from flask_cors import CORS, cross_origin
from mips_ALSH import Mips, HashFt, Hash_Table
from utils import _ranking, merged_dict

config_path = 'config.yaml'
hashft_path = 'hash_ft.pickle'

# ----------------- Load parameters-----------------

if config_path in os.listdir():
    with open(config_path, 'r') as f:
        params = yaml.load(f, Loader = yaml.FullLoader)
else:
    raise f"{config_path} does not exists"
# ----------------- ML part ----------------------
# Load google translator
translator = googletrans.Translator()

# Load model
model = torch.load('model.pth')
model.eval()
print("Sentence BERT loading complete.")

# --------------- Data Loading part -----------------

## hash functions
if hashft_path in os.listdir(os.path.join(os.getcwd(), 'gen_ids')):
    print("Previous hash funtion exists.. Loading hash function", end = '... ')
    with open(os.path.join('gen_ids',hashft_path), 'r') as f:
        hashft = yaml.load(f, Loader = yaml.FullLoader)
    print("Done.")
else:
    print(f"hashft_path: {hashft_path} does not exists. Create new hash function", end = '... ')
    hashft_class = HashFt(params)
    hashft = hashft_class.hash_functions
    print("Done.")

## stackoverflow data
print("Loading StackoverFlow Data...", end = ' ')
StackOverflow_Data = pd.read_csv('SOF_dbms.csv')
SO_title = [text for text in StackOverflow_Data['title']]
SO_body = [text for text in StackOverflow_Data['body']]

print("\tWait for preprocessing.", end = '... ')
SO_title_embedding = model.encode(SO_title, convert_to_tensor=True)
SO_body_embedding = model.encode(SO_body, convert_to_tensor=True)
SO_title_hash_table = Hash_Table(params, hashft, SO_title_embedding)
SO_title_Data = SO_title_hash_table.table
SO_body_hash_table = Hash_Table(params, hashft, SO_body_embedding)
SO_body_Data = SO_body_hash_table.table
print("Done.")

print("Stack Overflow Data Loading Complete.")

## etl data
print("Loading Peer Q&A Data...", end = ' ')
etl_Data = pd.read_csv('etl_Questions.csv')
etl_title = [text for text in etl_Data['title']]
etl_body = [text for text in etl_Data['content']]

print("\tWait for preprocessing.", end = '... ')
etl_title_embedding = model.encode(etl_title, convert_to_tensor=True)
etl_body_embedding = model.encode(etl_body, convert_to_tensor=True)
etl_title_hash_table = Hash_Table(params, hashft, etl_title_embedding)
etl_title_Data = etl_title_hash_table.table
etl_body_hash_table = Hash_Table(params, hashft, etl_body_embedding)
etl_body_Data = etl_body_hash_table.table
print("Done.")

print("ETL Data Loading Complete.")
search_engine = Mips(hashft, params)
print("***Search Engine Loading Complete. Recommendation Server is available from now.***\n")
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
        return jsonify(_ranking(request, search_engine, StackOverflow_Data, SO_title_Data, SO_body_Data, "StackOverFlow"))

@app.route('/etl',methods = ['POST', 'GET']) ## ETL data search engine
@cross_origin()
def etl_result():
    if request.method == 'GET':
        return jsonify(_ranking(request, search_engine, etl_Data, etl_title_Data, etl_body_Data, 'ETL'))

@app.route('/mixed',methods = ['POST', 'GET']) ## MIXED data search engine
@cross_origin()
def mixed_result():
    if request.method == 'GET':
        
        so_rank = _ranking(request, search_engine, StackOverflow_Data, SO_title_Data, SO_body_Data, 'StackOverFlow')
        etl_rank = _ranking(request, search_engine, etl_Data, etl_title_Data, etl_body_Data, 'ETL')
        
        ranking_dict = merged_dict(so_rank, etl_rank)
            
        return jsonify(ranking_dict)

if __name__ == '__main__':
    app.run(debug=True)
    
    """
    시나리오. 데모영상의 구체적인 시나리오.
    cherry pick을 보여주기. 어떤 데이터가 가장 이쁜가.
    
    
    데이터 가져오는 플라스크 서버 
    
    output을 json 형식으로 보내기
    
    """
    
