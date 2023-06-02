import os, yaml, pickle
import torch
from mips_ALSH import Mips, HashFt, Hash_Table

with open('config.yaml', 'r') as f:
    params = yaml.load(f, Loader = yaml.FullLoader)


if params['embedding_size'] == 384:
    model = torch.load('model.pth') 
elif params['embedding_size'] == 1024:
    model = torch.load('model_large.pth') 
model.eval()

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
    
