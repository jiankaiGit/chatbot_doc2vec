# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 23:21:30 2020

@author: jiank
"""
import gensim
from gensim.test.utils import common_texts
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.test.utils import get_tmpfile
import os
import jieba

#全域變數
stopwords = []
trainFilePath = "文本檔案/"          
allFilePaths = os.listdir(trainFilePath)
filePaths = []
documents = []
rawDocuments = []

#設定停用詞的函數
def setStopWords():
    with open('停用詞.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if len(line)>0:
                stopwords.append(line.strip())
#要訓練的檔案的前處理    
def preProcessData():
    #將所有檔案的路徑取出
    count = 0
    for fileName in allFilePaths:
        filePaths.append(trainFilePath+fileName)
        words = []
        with open(trainFilePath+fileName,'r',encoding='utf-8') as f:
            for line in f:

                # jieba分詞
                cut = jieba.cut(line)
                
                #停用詞過濾
                for word in cut:
                    if word not in stopwords and word != '\n':
                        words.append(word)
            # 填入TaggedDocument格式
            documents.append(gensim.models.doc2vec.TaggedDocument(words, [str(count)]))
            rawDocuments.append(words)
            count += 1
            print(words)
            print("------------")

                
#分析相似度
# wantAnalysisFile 想要分析的檔案
# topNear 幾個最相似的結果
# 訓練的模型
def mostSimilar(wantAnalysisFile, topNear, doc2vecModel):
    answer = ""
    with open(wantAnalysisFile, 'r', encoding='utf-8') as f:
        for line in f:
            if len(line)>0:
                answer += line.strip()

    analysisText = answer.split(' ')
    #取得向量
    inferred_vector = model.infer_vector(doc_words=analysisText,alpha=0.025,steps=300)
    #相似度比較 topn取出最相似的句數
    sims = model.docvecs.most_similar([inferred_vector],topn=topNear)
    return sims

import os
if __name__ == "__main__":
    #設定停用詞
    setStopWords()
    #處理要訓練的資料
    preProcessData()
    #訓練模型
    model = Doc2Vec(documents, vector_size=200, window=2, min_count=1, workers=4)
    #儲存模型
    model.save("doc2vec.model")
    #載入模型
    model = Doc2Vec.load("doc2vec.model")
    
    mostSims = mostSimilar("6.txt",10,model)
    print(mostSims)
    






