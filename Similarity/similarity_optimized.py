from collections import Counter
import pandas as pd
import re
import math
import numpy as np
import time
from multiprocessing import Pool, cpu_count, Manager
import torch

def tf(word, count):
    return count[word] / sum(count.values())

def n_containing(word, count_list):
    return sum(1 for count in count_list if word in count)

def idf(word, count_list):
    return math.log(len(count_list) / (1 + n_containing(word, count_list)))

def tfidf(word, count, count_list):
    return tf(word, count) * idf(word, count_list)

def words2vec(words):
    embeddings = []
    for word in words:
        if word in word_embedding:
            embeddings.append(word_embedding[word])

    if len(embeddings) != 0:
        return np.sum(embeddings, axis=0) / len(embeddings)
    else:
        return [0 for _ in range(200)]


def cosine_similarity(vector1, vector2):
    assert (len(vector1) == len(vector2))

    dot_product = 0.0
    normA = 0.0
    normB = 0.0
    for i in range(len(vector1)):
        dot_product += vector1[i] * vector2[i]
        normA += vector1[i] ** 2
        normB += vector2[i] ** 2
    if normA == 0.0 or normB == 0.0:
        return 0
    else:
        return round(dot_product / ((normA ** 0.5) * (normB ** 0.5)), 5)

# use GPU to calculate cosine similarity
# def cosine_similarity(vector1, vector2):
#     assert (len(vector1) == len(vector2))
#
#     vector1 = torch.FloatTensor(vector1).cuda()
#     vector2 = torch.FloatTensor(vector2).cuda()
#     dot_product = torch.matmul(vector1, vector2).item()
#     normA = torch.matmul(vector1, vector1).item()
#     normB = torch.matmul(vector2, vector2).item()
#     if normA == 0.0 or normB == 0.0:
#         return 0
#     else:
#         return round(dot_product / ((normA ** 0.5) * (normB ** 0.5)), 5)

max_workers = cpu_count()
print(max_workers)

stopfilepath='stopwords.txt'
stopwords=pd.read_csv(stopfilepath,header=None,sep='\n',encoding='utf-8',names=['stopword'],index_col=False, quoting=3)
stopwordslist=stopwords['stopword'].tolist()

essay_arrays = []
inputfile = open("199801_clear.txt","r",encoding="gbk")
inputfile_str = inputfile.read()
inputfile.close()

file_iterator = inputfile_str.split("\n\n")
for file in file_iterator:
    essay_arrays.append(file)

essay_words_arrays = []
countlist = []
for essay in essay_arrays:
    essay_words_list = []
    essay_iterator = essay.split("\n")
    for sentence in essay_iterator:
        sentence_iterator = sentence.split("  ")
        del sentence_iterator[0]
        for word in sentence_iterator:
            word = re.sub(r"/[A-Za-z]*","",word)
            if word not in stopwordslist and word != '':
                essay_words_list.append(word)

    essay_words_arrays.append(essay_words_list)
   
    count = Counter(essay_words_list)
    countlist.append(count)


TF_IDF_start = time.time()
TF_IDF_arrays = []

def cal_TF_IDF(i, count, dict):
    scores = {word: tfidf(word, count, countlist) for word in count}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    dict[i] = sorted_words[0:10]

pool = Pool(max_workers)
TF_IDF_dict = Manager().dict()
for i, count in enumerate(countlist):
    pool.apply_async(cal_TF_IDF, args=(i, count, TF_IDF_dict))
pool.close()
pool.join()
TF_IDF_dict = dict(TF_IDF_dict)
TF_IDF_end = time.time()

for i in range(len(TF_IDF_dict)):
    TF_IDF_arrays.append(dict(TF_IDF_dict[i]))
print(TF_IDF_arrays)

embedding_start = time.time()
all_words = set()
for TF_IDF_essay in TF_IDF_arrays:
    all_words.update(TF_IDF_essay.keys())
print(len(all_words))

word_embedding = {}
is_first_line = True
with open("Tencent_AILab_ChineseEmbedding.txt",encoding="utf-8") as fin:
    for line in fin:
        if is_first_line:
            is_first_line = False
            continue
        fields = line[:-1].split()
        if len(fields) != 201:
            continue
        word = fields[0]
        if word in all_words:
            word_embedding[word] = np.array([float(x) for x in fields[1:]])


# pool = Pool(max_workers)
# word_embedding = Manager().dict()
# fin = open("Tencent_AILab_ChineseEmbedding.txt",encoding="utf-8")
# next(fin)
#
# def cal_word_embedding(line, dict):
#     fields = line[:-1].split()
#     if len(fields) != 201:
#         return
#     word = fields[0]
#     if word in all_words:
#         dict[word] = np.array([float(x) for x in fields[1:]])
# count = 0
# for line in fin:
#     pool.apply_async(cal_word_embedding, args=(line, word_embedding))
#     count += 1
#     print(count)
# pool.close()
# pool.join()
# fin.close()
# word_embedding = dict(word_embedding)

doc_embedding = {}
for i in range(len(TF_IDF_arrays)):
    doc_embedding[i] = words2vec(TF_IDF_arrays[i].keys())
embedding_end = time.time()

similarity_start = time.time()
similarity_matrix = []
np.set_printoptions(threshold=np.inf) 
def cal_similarity_matrix(i, dict):
    similarity_array = np.zeros(len(TF_IDF_arrays))
    for j in range(len(TF_IDF_arrays)):
        if i == j:
            similarity_array[j] = 1
        elif i > j:
            similarity_array[j] = cosine_similarity(doc_embedding[i],doc_embedding[j])

    print(i, " / ", len(TF_IDF_arrays), " finished!")
    dict[i] = similarity_array

pool = Pool(max_workers)
similarity_dict = Manager().dict()
for i in range(len(TF_IDF_arrays)):
    pool.apply_async(cal_similarity_matrix, args=(i, similarity_dict))
pool.close()
pool.join()
similarity_dict = dict(similarity_dict)

similarity_end = time.time()

for i in range(len(TF_IDF_arrays)):
    similarity_matrix.append(similarity_dict[i])

for i in range(len(TF_IDF_arrays)):
    print(similarity_matrix[i])

with open("advanced_similarity_matrix.txt","w") as f:
    for i in range(len(TF_IDF_arrays)):
        f.write(str(similarity_matrix[i])+'\n')

print("The time of calculating TF-IDF:",TF_IDF_end - TF_IDF_start)
print("The time of calculating doc embedding:",embedding_end - embedding_start)
print("The time of calculating similarity matrix:",similarity_end - similarity_start)
