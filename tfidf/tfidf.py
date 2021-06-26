import os
import numpy as np
from collections import OrderedDict
import json
import argparse
from ckiptagger import WS
from tqdm import tqdm

import gensim
from gensim import corpora, models, similarities
from gensim.models import Phrases
from gensim.models.phrases import Phraser
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix, Similarity
from collections import OrderedDict

parser = argparse.ArgumentParser(description='TFIDF')
parser.add_argument('--ocr_file', type=str, help='path of image ocr results', default='./documents/ocrs.csv')
parser.add_argument('--tag_file', type=str, help='path of image tag results', default='./documents/tags.csv')
parser.add_argument('--text_file', type=str, help='path of image ocr and tag results', default='./documents/alls.csv')
parser.add_argument('--model_path', type=str, help='path to save tfidf model', default='./models')
parser.add_argument('--tagger_path', type=str, help='path to load CkipTagger model', default='data')

if __name__ == '__main__':
    args = parser.parse_args()
else:
    args = parser.parse_args([
        '--ocr_file', 'tfidf/documents/ocrs.csv',
        '--tag_file', 'tfidf/documents/tags.csv',
        '--text_file', 'tfidf/documents/alls.csv',
        '--model_path', 'tfidf/models',
        '--tagger_path', 'tfidf/data',
        ])

ws = WS(args.tagger_path, disable_cuda=False)

class TFIDF():
    def __init__(self, all_text_ocr, all_text_tag, all_text):
        self.doclen = len(all_text)
        self.imageId = np.array(list(all_text.keys()))
        self.ocrs = list(sorted(all_text_ocr.values()))
        self.tags = list(sorted(all_text_tag.values()))
        self.alls = list(sorted(all_text.values()))
        self.dictionary_ocr = corpora.Dictionary(self.ocrs)
        self.dictionary_tag = corpora.Dictionary(self.tags)
        self.dictionary_all = corpora.Dictionary(self.alls)
        self.corpus_ocr = [self.dictionary_ocr.doc2bow(text) for text in self.ocrs]
        self.corpus_tag = [self.dictionary_tag.doc2bow(text) for text in self.tags]
        self.corpus_all = [self.dictionary_all.doc2bow(text) for text in self.alls]
        self.featureNum_ocr = len(self.dictionary_ocr.token2id.keys())
        self.featureNum_tag = len(self.dictionary_tag.token2id.keys())
        self.featureNum_all = len(self.dictionary_all.token2id.keys())
        self.ws = WS(args.tagger_path, disable_cuda=False)

        # array for permuting scores
        self.permute = np.argsort(self.imageId)

    def build_models(self, model_path=None):
        if os.path.exists(model_path+'/tfidf_all.mm'):
            print("[*] load models from", model_path, "...")
            self.tfidf_ocr = models.TfidfModel.load(model_path+'/tfidf_ocr.mm')
            self.tfidf_tag = models.TfidfModel.load(model_path+'/tfidf_tag.mm')
            self.tfidf_all = models.TfidfModel.load(model_path+'/tfidf_all.mm')
        else:
            print("[*] no pre-model found, creating new models...")
            # ocr
            pivot = 0
            for bow in self.corpus_ocr:
                pivot += len(bow)
            pivot /= len(self.corpus_ocr)
            self.tfidf_ocr = models.TfidfModel(self.corpus_ocr, id2word=self.dictionary_ocr, smartirs="Ltc", pivot=pivot, slope=0.2)
            self.tfidf_ocr.save(model_path+'/tfidf_ocr.mm')

            # tag
            pivot = 0
            for bow in self.corpus_tag:
                pivot += len(bow)
            pivot /= len(self.corpus_tag)
            self.tfidf_tag = models.TfidfModel(self.corpus_tag, id2word=self.dictionary_tag, smartirs="Ltc", pivot=pivot, slope=0.2)
            self.tfidf_tag.save(model_path+'/tfidf_tag.mm')

            # ocr
            pivot = 0
            for bow in self.corpus_all:
                pivot += len(bow)
            pivot /= len(self.corpus_all)
            self.tfidf_all = models.TfidfModel(self.corpus_all, id2word=self.dictionary_all, smartirs="Ltc", pivot=pivot, slope=0.2)
            self.tfidf_all.save(model_path+'/tfidf_all.mm')
            
        self.tfidf_corpus_ocr = self.tfidf_ocr[self.corpus_ocr]
        self.tfidf_corpus_tag = self.tfidf_tag[self.corpus_tag]
        self.tfidf_corpus_all = self.tfidf_all[self.corpus_all]

        if os.path.exists(model_path+'/index_all.mm'):
            print("[*] load index model from", model_path, "...")
            self.index_ocr = similarities.MatrixSimilarity.load(model_path+'/index_ocr.mm')
            self.index_tag = similarities.MatrixSimilarity.load(model_path+'/index_tag.mm')
            self.index_all = similarities.MatrixSimilarity.load(model_path+'/index_all.mm')
        else:
            print("[*] no pre-model found, creating new index model...")
            self.index_ocr = similarities.SparseMatrixSimilarity(self.tfidf_corpus_ocr, num_features=self.featureNum_ocr)
            self.index_tag = similarities.SparseMatrixSimilarity(self.tfidf_corpus_tag, num_features=self.featureNum_tag)
            self.index_all = similarities.SparseMatrixSimilarity(self.tfidf_corpus_all, num_features=self.featureNum_all)
            self.index_ocr.save(model_path+'/index_ocr.mm')
            self.index_tag.save(model_path+'/index_tag.mm')
            self.index_all.save(model_path+'/index_all.mm')

    def get_tfidf(self, texts):
        texts = self.ws( [texts] )
        vec_bow_ocr, vec_bow_tag, vec_bow_all = self.get_bow(texts[0])
        return self.tfidf_ocr[vec_bow_ocr], self.tfidf_tag[vec_bow_tag], self.tfidf_all[vec_bow_all]

    def retrieve(self, query, k=10):
        qtf_ocr, qtf_tag, qtf_all = self.get_tfidf(query)
        qindices_ocr = self.index_ocr[qtf_ocr]
        qindices_tag = self.index_tag[qtf_tag]
        qindices_all = self.index_all[qtf_all]
        sorted_indices_ocr = np.argsort(qindices_ocr)[::-1][:k]
        sorted_indices_tag = np.argsort(qindices_tag)[::-1][:k]
        sorted_indices_all = np.argsort(qindices_all)[::-1][:k]
        topk_scores_ocr = qindices_ocr[sorted_indices_ocr]
        topk_scores_tag = qindices_tag[sorted_indices_tag]
        topk_scores_all = qindices_all[sorted_indices_all]
        return sorted_indices_ocr, sorted_indices_tag, sorted_indices_all, topk_scores_ocr, topk_scores_tag, topk_scores_all

    def get_bow(self, texts):
        vec_bow_ocr = self.dictionary_ocr.doc2bow(texts)
        vec_bow_tag = self.dictionary_tag.doc2bow(texts)
        vec_bow_all = self.dictionary_all.doc2bow(texts)
        return vec_bow_ocr, vec_bow_tag, vec_bow_all
    
    def get_result(self, idx, mode='all'):
        if mode == 'ocr':
            return self.imageId[idx], self.ocrs[idx]
        elif mode == 'tag':
            return self.imageId[idx], self.tags[idx]
        else:
            return self.imageId[idx], self.alls[idx]

    def score(self, query):
        qtf_ocr, qtf_tag, qtf_all = self.get_tfidf(query)
        qindices_ocr = self.index_ocr[qtf_ocr]
        qindices_tag = self.index_tag[qtf_tag]
        qindices_all = self.index_all[qtf_all]
        return qindices_ocr[self.permute], qindices_tag[self.permute], qindices_all[self.permute]
            
all_text_ocr = dict()
all_text_tag = dict()
all_text_all = dict()

with open(args.ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines[1:]:
    parts = line.split(',')
    imageID = int(parts[0])
    texts = parts[1].replace('\n', '').split(" ")
    all_text_ocr[imageID] = texts
    
with open(args.tag_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines[1:]:
    parts = line.split(',')
    imageID = int(parts[0])
    texts = parts[1].replace('\n', '').split(" ")
    all_text_tag[imageID] = texts

with open(args.text_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines[1:]:
    parts = line.split(',')
    imageID = int(parts[0])
    texts = parts[1].replace('\n', '').split(" ")
    all_text_all[imageID] = texts
    
tfidf = TFIDF(all_text_ocr, all_text_tag, all_text_all)
tfidf.build_models(args.model_path)

print("[*] there are total {} terms in the {} documents".format(tfidf.featureNum_all, tfidf.doclen))

if __name__ == '__main__':
    try:
        k = int(input("number of retrieved documents(default 10): "))
    except:
        k = 10

    while True:
        query = input("query: ")
        indices_ocr, indices_tag, indices_all, scores_ocr, scores_tag, scores_all = tfidf.retrieve(query, k)
        print('\n------result_ocr------')
        for i in range(k):
            idx, rt = tfidf.get_result(indices_ocr[i], mode='ocr')
            print("{}\t: {:.8f}\t{}".format(idx, scores_ocr[i], ''.join(rt)))
        print('\n------result_tag------')
        for i in range(k):
            idx, rt = tfidf.get_result(indices_tag[i], mode='tag')
            print("{}\t: {:.8f}\t{}".format(idx, scores_tag[i], ''.join(rt)))
        print('\n------result_all------')
        for i in range(k):
            idx, rt = tfidf.get_result(indices_all[i], mode='all')
            print("{}\t: {:.8f}\t{}".format(idx, scores_all[i], ''.join(rt)))
        print("------------------\n")

