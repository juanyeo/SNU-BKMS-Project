import yaml
import torch
import pickle
from scipy.spatial.distance import cosine

with open('config.yaml', 'r') as f:
    params = yaml.load(f, Loader = yaml.FullLoader)

class Mips():
    """
    Maximum inner product search: 주어진 쿼리 벡터에 대하여 내적값이 큰 다른 벡터들을 빠르게 찾을 수 있는 방법.    
    """
    def __init__(self, hash_functions, params):
        self.params = params
        self.hash_functions = hash_functions
        self.hashNum = self.params['hash_num']
        self.m = self.params['m']
        self.emb_rank_size = params['emb_ranking_size']
        
    def search(self, text, query, titleData, bodyData, is_normalized = False):
        """
        Return the rankings of Data indices
        
        Args:
            query: 자연어 아님. 자연어를 모델에 넣어서 나온 임베딩 벡터(embedder 모델의 아웃풋)
                query shape: (1, embedding_dim)
            Data: 전처리 완료된 데이터. Maximum inner product search를 위하여 expanded & normalized & hash mapping 되어있어야 함.
                Data shape: (Data Size, number of hash function)
                
        returns:
            충돌이 가장 많이 일어난(내적값이 가장 크다고 판단된) 데이터 중
            self.emb_rank_size 개수만큼의 데이터에 대한 인덱스를 반환함.
        """
        Q = self.expand_q(query) # shape: (1, embedding_dim + self.m)
        hash_mapped = self.hash_functions(Q) # shape: (1, number of hash function) -> hash 함수 통하여 정수형 벡터로 변환
        title_collision = torch.sum(torch.where((hash_mapped - titleData)==0, True, False), 1).reshape(-1)
        body_collision = torch.sum(torch.where((hash_mapped - bodyData)==0, True, False), 1).reshape(-1)
        sorted, indices = torch.sort(title_collision + 3*body_collision)
        ranking = indices[-self.emb_rank_size:]
        
        return ranking, sorted[-self.emb_rank_size:]
        
    
    def expand_q(self, Q):    
        """
        Assume that the shape of Q is (1, embedding_dim)
        """
        return torch.concatenate([Q, torch.zeros((1, self.m))], 1)

class HashFt():
    def __init__(self, params, hash_functions = None):
        self.params = params
        self.hash_num = self.params['hash_num']
        self.r = self.params['r']
        self.emb_dim = params['embedding_size']
        self.m = self.params['m']
        if hash_functions == None:
            self.hash_functions = self.gen_hashfts()
            # self.save_hashft()
        else:
            self.hash_functions = hash_functions
            
    def gen_hashfts(self):
        """
        return: hash functions
        output shape = (self.hash_nums, self.dim)
        
        cf: 이 해시함수는 나중에 어떻게 사용되는가
        우리가 갖고 있는 데이터 x에 대하여
        (data_size, self.hash_nums) 차원을 갖는 벡터인 (A*X + B)/r을 미리 계산하고, 
        이 값들의 소수부분을 날린 정수형 벡터를 데이터베이스에 저장함.
        
        쿼리가 날라올 때마다 이 똑같은 해시함수에 통과시켜서 정수부분을 추출하고, 
        해시함수 개수만큼의 결과값 중 그 수가 가장 많이 겹치는 데이터들을 대상으로 랭킹을 매겨 추천.
        """
        self.A = torch.randn(self.hash_num, self.emb_dim + self.m)
        self.B = torch.rand(size = (1, self.hash_num)) * self.r
        
        def hashft(Data):
            """ 해시함수

            Args:
                Data (torch.tensor): shape=(Data_size, self.emb_dim + self.m)
                A (torch.tensor, optional): _description_. Defaults to self.A. shape=(self.hash_num, self.meb_dim + self.m)
                B (torch.tensor, optional): _description_. Defaults to self.B. shape=(self.hash_num)
                r (int, optional): _description_. Defaults to self.r.

            Returns:
                _type_: _description_ shape=(Data_size, hash_num)
            """

            return torch.floor((Data @ self.A.T + self.B)/self.r) 
        
        return hashft
    
    def save_hashft(self):
        if not self.hash_functions:
            raise "No hash function"
        with open(self.params['hash_ft_path'], 'wb') as f:
            pickle.dump(self.hash_functions, f)
            
class Hash_Table():
    def __init__(self, params, hash_function, table = None):
        self.params = params
        self.m = params['m']
        self.hash_function = hash_function
        if table == None:
            try:
                with open(self.parmas['hash_table_path'], 'rb') as f:
                    self.table = pickle.load(f)
            except:
                print("we done't have saved hash_table.")
                nothing = True
        else:
            self.table = table
        if not self.hashness_check():
            # print("Current data is not completely preprocessed. Wait for preprocessing.")
            self.table = self.emb2hs()
            print("Preprocessing Done.")
    def hashness_check(self):
        if type(self.table) != list:
            return False
        if len(self.table) == 0 or type(self.table[0])!=list:
            return False
        if len(self.table[0]) == 0 or self.table[0][0] != int(self.table[0][0]):
            return False
        if set([len(t[0]) for t in self.table])!=1:
            return False
        return True
    
    def expand(self):
        """
        args: embedded data. shape:(data_size, emb_size)
        """
        max_vecnorm = torch.max(torch.norm(self.table, dim = 1))
        self.table = self.table / max_vecnorm
        added = torch.Tensor([[0.5-torch.norm(v)**(2**i) for i in range(1, self.m+1)] for v in self.table])
        
        expanded = torch.concat([self.table, added], dim = 1)
        
        return expanded

    def emb2hs(self):
        return self.hash_function(self.expand())
        
def jacarrd_sim():
    return