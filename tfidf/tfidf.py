import os
import numpy as np
from collections import OrderedDict
import json
import argparse
from ckiptagger import WS

import gensim
from gensim import corpora, models, similarities
from gensim.models import Phrases
from gensim.models.phrases import Phraser
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix, Similarity
from collections import OrderedDict

parser = argparse.ArgumentParser(description='TFIDF')
parser.add_argument('--text_file', required=True, type=str, help='path of image ocr results')
parser.add_argument('--tfidf_path', required=True, type=str, help='path to save tfidf model')
parser.add_argument('--index_path', required=True, type=str, help='path to save index model')

args = parser.parse_args() 

class TFIDF():
    def __init__(self, all_text):
        self.doclen = len(all_text)
        self.imageId = list(all_text.keys())
        self.all_text = list(all_text.values())
        self.dictionary = corpora.Dictionary(self.all_text)
        self.corpus = [self.dictionary.doc2bow(text) for text in self.all_text]
        self.featureNum = len(self.dictionary.token2id.keys())
        self.ws = WS('./data', disable_cuda=False)

    def build_models(self, tfidf_path=None, index_path=None):
        if tfidf_path and os.path.exists(tfidf_path):
            print("[*] load tfidf model from", tfidf_path, "...")
            self.tfidf = models.TfidfModel.load(tfidf_path)
        else:
            print("[*] no pre-model found, creating new tfidf model...")
            pivot = 0
            for bow in self.corpus:
                pivot += len(bow)
            pivot /= len(self.corpus)
            self.tfidf = models.TfidfModel(self.corpus, id2word=self.dictionary, smartirs="Ltc", pivot=pivot, slope=0.2)
            self.tfidf.save(tfidf_path)
        self.tfidf_corpus = self.tfidf[self.corpus]
        if index_path and os.path.exists(index_path):
            print("[*] load index model from", index_path, "...")
            self.index = similarities.MatrixSimilarity.load(index_path)
        else:
            print("[*] no pre-model found, creating new index model...")
            self.index = similarities.SparseMatrixSimilarity(self.tfidf_corpus, num_features=self.featureNum)
            self.index.save(index_path)
    
    def get_tfidf(self, texts):
        texts = self.ws( [texts] )
        vec_bow = self.get_bow(texts[0])
        return self.tfidf[vec_bow]

    def retrieve(self, query, k=10):
        qtf = self.get_tfidf(query)
        qindices = self.index[qtf]
        sorted_indices = np.argsort(qindices)[::-1][:k]
        topk_scores = qindices[sorted_indices]
        return sorted_indices, topk_scores

    def get_bow(self, texts):
        vec_bow = self.dictionary.doc2bow(texts)
        return vec_bow
    
    def get_result(self, idx):
        return self.imageId[idx], self.all_text[idx]
            
if __name__ == '__main__':
    all_text = dict()
    with open(args.text_file, 'r') as f:
        lines = f.readlines()

    for line in lines:
        parts = line.split(',')
        imageID = parts[0]
        texts = parts[1].replace('\n', '').split(" ")
        all_text[imageID] = texts

    tfidf = TFIDF(all_text)
    tfidf.build_models(args.tfidf_path, args.index_path)
    print("[*] there are total {} terms in the {} documents".format(tfidf.featureNum, tfidf.doclen))
    
    try:
        k = int(input("number of retrieved documents(default 10): "))
    except:
        k = 10

    while True:
        query = input("query: ")
        indices, scores = tfidf.retrieve(query, k)
        print('\n------result------')
        for i in range(k):
            idx, rt = tfidf.get_result(indices[i])
            print("{}\t: {:.8f}\t{}".format(idx, scores[i], ''.join(rt)))
        print("------------------\n")
