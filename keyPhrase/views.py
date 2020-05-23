from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

import jieba
import jieba.analyse
from index.models import News, Author, Parent, Children, keyInformation
import copy
import nltk
import itertools, string
from nltk.stem.porter import *
import numpy as np
from langdetect import detect
import jieba
import jieba.posseg as pseg
import re
import os

LTP_DATA_DIR = 'C:/Users/david/Desktop/site/django site/knowledge/ltp_data_v3.4.0'

class ChineseExtractionView(TemplateView):
    template_name = "searching/results.html"

    def get(self, request):
        all_news = News.objects.all()

        for new in all_news:
            if detect(new.title) == 'zh-cn' or detect(new.title) == 'zh':
                the_news_content = new.content
                the_news_keywords = new.keywords.all()

                text = copy.deepcopy(the_news_content)

                # 分词
                # a = time.time()
                cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
                from pyltp import Segmentor
                segmentor = Segmentor()  # 初始化实例
                segmentor.load(cws_model_path)  # 加载模型
                words = segmentor.segment(text)  # 分词
                words_list = list(words)
                print(words_list)
                segmentor.release()  # 释放模型
                # 词性标注
                pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
                from pyltp import Postagger

                postagger = Postagger()  # 初始化实例
                postagger.load(pos_model_path)  # 加载模型

                words = words_list  # 分词结果
                postags = postagger.postag(words)  # 词性标注
                postags_list = list(postags)
                print(postags_list)
                postagger.release()  # 释放模型
                # print(time.time() - a)

                # 命名实体识别
                ner_model_path = os.path.join(LTP_DATA_DIR, 'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`

                from pyltp import NamedEntityRecognizer

                recognizer = NamedEntityRecognizer()  # 初始化实例
                recognizer.load(ner_model_path)  # 加载模型

                words = words_list
                postags = postags_list
                netags = recognizer.recognize(words, postags)  # 命名实体识别
                netags_list = list(netags)
                print(netags_list)

                for index in range(len(netags_list)):
                    if netags_list[index].startswith('S'):
                        print(words_list[index])
                recognizer.release()  # 释放模型
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)


class EnglishExtractionView(TemplateView):
    template_name = "searching/results.html"

    def EnglishKeyPhraseExtraction(self, topk):
        for keyword in keyInformation.objects.all():
            for i in keyInformation.objects.filter(key_information=keyword).all():
                i.delete()
        all_news = News.objects.all()[:10]
        for new in all_news:
            if len(new.keywords.all()) > 0:
                print('keyword already filled')
                pass
            else:
                the_news_content = new.content
                the_news_keywords = new.keywords.all()

                text = copy.deepcopy(the_news_content)

                # text = ' '.join(text)
                candidates = []
                stemmer = PorterStemmer()
                text = stemmer.stem(text)
                grammer = r'KT: {(<JJ>* <NN.*>+ <IN>)? <JJ>* <NN.*>+}'

                punct = set(string.punctuation)
                stop_words = set(nltk.corpus.stopwords.words('english'))
                chunker = nltk.chunk.regexp.RegexpParser(grammer)
                tagged_sents = nltk.pos_tag_sents(nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(text))

                for i in range(len(tagged_sents)):
                    all_chunks = nltk.chunk.tree2conlltags(chunker.parse(tagged_sents[i]))
                    c = itertools.groupby(all_chunks, key=lambda x: x[2])
                    candid = [' '.join(x[0] for x in group) for key, group in
                              itertools.groupby(all_chunks, lambda x: x[2] != 'O') if key]
                    candidates = candidates + candid

                candidates = list(set(candidates))

                cand = np.array(candidates)
                cand_set = set(candidates)
                A = np.zeros([len(cand), len(cand)])

                punct = string.punctuation
                punct = set(punct)
                punct.add('``')
                punct.add("''")
                text = nltk.word_tokenize(text)
                text = ' '.join(text)
                # doc = [word for word in text if word not in punct]
                # doc=np.array(doc)
                i = 0
                for word in cand:
                    try:
                        words = nltk.word_tokenize(word)
                        start_d = [m.start() for m in
                                   re.finditer(word + ' ', text)]  # start_d = np.where(doc==words[0])[0]
                        end_d = [m.end() for m in re.finditer(word + ' ', text)]  # end_d = np.where(doc==words[-1])[0]
                        d_in = min(start_d)
                        j = 0
                    except:
                        pass
                    for other in cand:
                        try:
                            others = nltk.word_tokenize(other)
                            start_o = [m.end() for m in
                                       re.finditer(other + ' ', text)]  # start_o = np.where(doc==others[0])[0]
                            end_o = [m.end() for m in re.finditer(other + ' ', text)]  # np.where(doc==others[-1])[0]
                            d_st = np.abs([np.array(start_d) - end for end in end_o])
                            d_en = np.abs([np.array(end_d) - start for start in start_o])
                            d_tot = min(min(d_en[0]), min(d_st[0]))
                            A[i, j] = 1 / (d_tot) + 1 / (d_in + 1)
                            if d_tot == 0:
                                A[i, j] = 0
                            j = j + 1
                        except:
                            pass
                    i = i + 1

                l = A.shape[0]
                D = np.zeros([l, l])
                one = np.ones(l)
                for i in range(l):
                    D[i, i] = np.sum(A[i, :])
                x = np.dot(np.dot(D, np.linalg.pinv(D - 0.85 * A)), one)

                x_sort = np.sort(x)
                keywords = []

                print(new.title)
                for i in range(len(cand)):
                    j = np.where(x == x_sort[-(i + 1)])[0]
                    print(cand[j][0])
                for i in range(topk):
                    j = np.where(x == x_sort[-(i + 1)])[0]
                    if len(cand[j][0]) <= 4:
                        pass
                    else:
                        keywords.append(cand[j][0])
                for keyword in keywords:
                    if keyInformation.objects.filter(key_information=keyword):
                        keyword_temp = keyInformation.objects.get(key_information=keyword)
                    else:
                        keyword_temp = keyInformation(key_information=keyword)
                        keyword_temp.save()
                    new.keywords.add(keyword_temp)

    def get(self, request):
        all_news = News.objects.all()
        key_phrase = self.EnglishKeyPhraseExtraction(topk=20)
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
