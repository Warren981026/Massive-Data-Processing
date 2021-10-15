from collections import Counter
import pandas as pd
import re
import math
import numpy as np
import time

# calculate the TF-IDF
def tf(word, count):
    return count[word] / sum(count.values())

def n_containing(word, count_list):
    return sum(1 for count in count_list if word in count)

def idf(word, count_list):
    return math.log(len(count_list) / (1 + n_containing(word, count_list)))

def tfidf(word, count, count_list):
    return tf(word, count) * idf(word, count_list)

# word embedding
def words2vec(words):
    embeddings = []
    for word in words:
        if word in word_embedding:
            embeddings.append(word_embedding[word])

    if len(embeddings) != 0:
        return np.sum(embeddings, axis=0) / len(embeddings)
    else:
        return [0 for i in range(200)]

# calculate cosine similarity
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


# set stopwords
stopfilepath='stopwords.txt'
stopwords=pd.read_csv(stopfilepath,header=None,sep='\n',encoding='utf-8',names=['stopword'],index_col=False, quoting=3)
stopwordslist=stopwords['stopword'].tolist()

# upload inputfile
essay_arrays = []
inputfile = open("199801_clear.txt","r",encoding="gbk")
inputfile_str = inputfile.read()
inputfile.close()

# split different essays
file_iterator = inputfile_str.split("\n\n")
for file in file_iterator:
    essay_arrays.append(file)

essay_words_arrays = []
countlist = []
for essay in essay_arrays:
    # split words
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
    # count word frequency
    count = Counter(essay_words_list)
    countlist.append(count)

# calculate TF-IDF values
# choose Top10 words as key words
TF_IDF_start = time.time()
TF_IDF_arrays = []
for i, count in enumerate(countlist):
    scores = {word: tfidf(word, count, countlist) for word in count}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    TF_IDF_arrays.append(dict(sorted_words[0:10]))
TF_IDF_end = time.time()
print(TF_IDF_arrays)

# build set of candidate words
embedding_start = time.time()
all_words = set()
for TF_IDF_essay in TF_IDF_arrays:
    all_words.update(TF_IDF_essay.keys())
print(len(all_words))

# word embedding
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

# doc embedding
doc_embedding = {}
for i in range(len(TF_IDF_arrays)):
    doc_embedding[i] = words2vec(TF_IDF_arrays[i].keys())
embedding_end = time.time()

# calculate similarity
similarity_start = time.time()
similarity_matrix = np.zeros((len(TF_IDF_arrays),len(TF_IDF_arrays)))
np.set_printoptions(threshold=np.inf) # threshold 指定超过多少使用省略号，np.inf代表无限大
for i in range(len(TF_IDF_arrays)):
    for j in range(len(TF_IDF_arrays)):
        if i == j:
            similarity_matrix[i][j] = 1
        elif i > j:
            similarity_matrix[i][j] = cosine_similarity(doc_embedding[i],doc_embedding[j])

    print(i, " / ", len(TF_IDF_arrays), " finished!")

similarity_end = time.time()

for i in range(len(TF_IDF_arrays)):
    print(similarity_matrix[i])

similarity_matrix = similarity_matrix.tolist()

# output the similarity matrix
with open("similarity_matrix.txt","w") as f:
    for i in range(len(TF_IDF_arrays)):
        f.write(str(similarity_matrix[i])+'\n')

print("The time of calculating TF-IDF:",TF_IDF_end - TF_IDF_start)
print("The time of calculating doc embedding:",embedding_end - embedding_start)
print("The time of calculating similarity matrix:",similarity_end - similarity_start)
