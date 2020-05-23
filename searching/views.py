# -*- coding: utf-8 -*-

from uuid import uuid4
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseRedirect
from newspaper import news_pool

from index.models import ScrapyItem
from searching.forms import SearchForm
from newspaper import Article
import newspaper
from index.models import News, Author, Parent, Children, keyInformation
from langdetect import detect
import heapq
import inflect
import copy
import nltk
import itertools, string
from nltk.stem.porter import *
import numpy as np

p = inflect.engine()


class SearchView(TemplateView):
    template_name = "searching/searching.html"

    def all_in_keywords(self, search_words_weight, all_keywords):
        word = ''
        print(all_keywords)
        for i in all_keywords:
            try:
                detect(i)
                word = i
            except:
                continue
            if detect(word) == 'zh-cn':
                for keyword in all_keywords:
                    for search_word in search_words_weight:
                        num = keyword.count(search_word)
                        if num >= int(search_words_weight[search_word]):
                            pass
                        else:
                            return False
                return True
            else:
                return self.all_in_keywords_English(search_words_weight, all_keywords)

    def all_in_keywords_English(self, search_words_weight, all_keywords):
        list_search_words_weight = list(search_words_weight)
        results = []
        for index in range(len(list_search_words_weight)):
            results.append(False)
        for keyword in all_keywords:
            for index in range(len(list_search_words_weight)):
                if list_search_words_weight[index] in keyword:
                    results[index] = True
                else:
                    pass
        final_result = True
        for result in results:
            final_result = final_result and result
        return final_result

    def all_in_title(self, search_words_weight, title):
        for search_word in search_words_weight:
            if search_word in title:
                pass
            else:
                return False
        return True

    def selected_scrapy(self, article, search_key_weight):
        try:
            article.parse()
            article.nlp()
        except:
            return
        if self.all_in_title(search_key_weight, article.title) or \
                self.all_in_keywords(search_key_weight, article.keywords):
            self.scrapy(article)

    def all_scrapy(self, article, search_key_weight):
        self.scrapy(article)

    def scrapy(self, article):
        try:
            article.parse()
            article.nlp()
        except:
            return
        new_temp = News(title=article.title,
                            href=article.url,
                            time=article.publish_date,
                            content=article.text,
                            summary=article.summary)
        if News.objects.filter(title=article.title):
            return False
        else:
            new_temp.save()
            print('found')
            for author in article.authors:
                author_temp = Author(name=author)
                author_temp.save()
                new_temp.authors.add(author_temp)
                new_temp.save()

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        form = SearchForm(request.POST)
        if form.is_valid():
            search_key = form.cleaned_data['search_keys']
            search_weight = form.cleaned_data['search_weight']
            search_key = search_key.split(',')
            search_weight = search_weight.split(',')
            search_key_weight = {}
            for l in range(len(search_key)):
                search_key_weight[search_key[l]] = search_weight[l]
            if detect(search_key[0]) != 'zh' and detect(search_key[0]) != 'zh-cn':
                # cnn_paper = newspaper.build('http://cnn.com', memoize_articles=False)
                # print(cnn_paper.size())
                # times_paper = newspaper.build('https://www.nytimes.com/', memoize_articles=False)
                # print(times_paper.size())
                # guardian_paper = newspaper.build('https://www.theguardian.com/us', memoize_articles=False)
                # print(guardian_paper.size())
                # abc_paper = newspaper.build('https://abcnews.go.com/', memoize_articles=False)
                # print(abc_paper.size())
                # bbc_paper = newspaper.build('https://www.bbc.com/', memoize_articles=False)
                # print(bbc_paper.size())
                boston_paper = newspaper.build('https://www.bostonglobe.com//', memoize_articles=False)
                print(boston_paper.size())
                seattle_paper = newspaper.build('https://www.seattletimes.com/', memoize_articles=False)
                print(seattle_paper.size())
                # papers = [cnn_paper, times_paper, guardian_paper, abc_paper, bbc_paper]
                papers = [boston_paper, seattle_paper]
                news_pool.set(papers, threads_per_source=2)  # (5*2) = 10 threads total
                news_pool.join()
                # for article in cnn_paper.articles:
                #     self.all_scrapy(article, search_key_weight)
                # for article in times_paper.articles:
                #     self.all_scrapy(article, search_key_weight)
                # for article in guardian_paper.articles:
                #     self.all_scrapy(article, search_key_weight)
                # for article in abc_paper.articles:
                #     self.all_scrapy(article, search_key_weight)
                # for article in bbc_paper.articles:
                #     self.all_scrapy(article, search_key_weight)
                for article in boston_paper.articles:
                    self.all_scrapy(article, search_key_weight)
                for article in seattle_paper.articles:
                    self.all_scrapy(article, search_key_weight)
            elif detect(search_key[0]) == 'zh-cn':
                qq_paper = newspaper.build('https://www.qq.com/', memoize_articles=False)
                print('qq_paper: ' + str(qq_paper.size()))
                # wy_paper = newspaper.build('https://news.163.com/', memoize_articles=False)
                # papers = [qq_paper, wy_paper]
                papers = [qq_paper]
                news_pool.set(papers, threads_per_source=2)  # (3*2) = 6 threads total
                news_pool.join()
                for article in qq_paper.articles:
                    print('processing')
                    self.all_scrapy(article, search_key_weight)
                # for article in wy_paper.articles:
                #     print('processing')
                #     self.all_scrapy(article, search_key_weight)
        else:
            form = SearchForm()
        return HttpResponseRedirect(reverse('searching:results', args=()))


class ResultsView(TemplateView):
    template_name = "searching/results.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        return render(request, self.template_name)
