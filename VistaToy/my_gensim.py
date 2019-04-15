import jieba
import gensim
from gensim import corpora
from gensim import models
from gensim import similarities
from setting import MONGODB


l1 = list(MONGODB.content.find())
all_doc_list = []
for doc in l1: # doc = "你的名字是什么"
    doc_list = [word for word in jieba.cut_for_search(doc.get("title"))]
    all_doc_list.append(doc_list)

dictionary = corpora.Dictionary(all_doc_list)
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
lsi = models.LsiModel(corpus)
index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))

def my_xishujuzhenxiangsidu(a):
    doc_test_list = [word for word in jieba.cut_for_search(a)]
    doc_test_vec = dictionary.doc2bow(doc_test_list)
    sim = index[lsi[doc_test_vec]]
    cc = sorted(enumerate(sim), key=lambda item: -item[1])
    if cc[0][1] >= 0.75:
        text = l1[cc[0][0]]
    else:
        text = None


    return text