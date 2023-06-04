import os, yaml, pickle, random
import torch
import googletrans
from mips_ALSH import Mips, HashFt, Hash_Table
translator = googletrans.Translator()


with open('config.yaml', 'r') as f:
    params = yaml.load(f, Loader = yaml.FullLoader)


if params['embedding_size'] == 384:
    model = torch.load('model.pth') 
elif params['embedding_size'] == 1024:
    model = torch.load('model_large.pth') 
model.eval()


def _ranking(request, search_engine, Data, title_table, body_table, ranking_mode):
    question = request.args["question_title"]
    question = translator.translate(question, dest = 'en').text
    ranking, _ = search_engine.search(question, model.encode([question], convert_to_tensor = True), title_table, body_table)
    
    if ranking_mode == 'StackOverFlow':
        ranking_dict = {"www.stackoverflow.com/questions/"+str(Data['id'][int(ranking[-i-1])]):Data['title'][int(ranking[-i-1])] for i in range(len(ranking))} 
    elif ranking_mode == 'ETL':
        ranking_dict = {"/detail/"+str(Data['id'][int(ranking[-i-1])]):Data['title'][int(ranking[-i-1])] for i in range(len(ranking))}         
    else:
        raise "Invalid Data mode. Mode must be one of : 'StackOverFlow' or 'ETL'"
    return ranking_postprocess(question, ranking_dict, params['ranking_size'])

def gen_DataTable(embedding, fileLoc, hashft):
    if fileLoc in os.listdir():
        with open(fileLoc, 'rb') as fr:
            Data = pickle.load(fr)
        print(f"{fileLoc} already exist. Loaded {fileLoc}")
    else:
        print(f"{fileLoc} does not exist. Start to generate {fileLoc}", end = ' ')
        hash_table = Hash_Table(params, hashft, embedding)
        Data = hash_table.table
        print('...', end = '')
        with open(fileLoc,"wb") as fw:
            pickle.dump(Data, fw)
        print("Done.")
    return Data
    

def gen_embedding(data, fileLoc):

    if fileLoc in os.listdir():
        with open(fileLoc, 'rb') as fr:
            embedding = pickle.load(fr)
        print(f"{fileLoc} already exist. Loaded fileLoc")
    else:
        print(f"{fileLoc} does not exist. Start to generate {fileLoc}", end = ' ')
        print('...', end = '')
        embedding = model.encode(data, convert_to_tensor=True)
        with open(fileLoc,"wb") as fw:
            pickle.dump(embedding, fw)
        print("Done.")
    return embedding
    
def ranking_postprocess(question , ranking, final_num):
    ranking_list = list(ranking.items())
    for i in range(len(ranking_list)):
        ranking_list[i] = (jaccard_sim(question, ranking_list[i][1]), i, ranking_list[i][0], ranking_list[i][1])
    ranking_list.sort(reverse=True)
    ranking_list = ranking_list[:final_num]
    ranking = {r[2]:r[3] for r in ranking_list}
    return ranking
    
    
def jaccard_sim(textA, textB)-> float:
    tA, tB = set(textA.lower().split()), set(textB.lower().split())
    if len(tA) == len(tB) == 0:
        return 0
    return len(tA & tB) / len(tA | tB)
    


def merged_dict(dict1, dict2):
    merged = {}
    for key, val in dict1.items():
        merged[key] = val
    for key, val in dict2.items():
        merged[key] = val
    
    merged = list(merged.items())
    random.shuffle(merged)
    merged = dict(merged)
    return merged    
