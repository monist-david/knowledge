import nltk
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
from nltk import word_tokenize, PorterStemmer, sent_tokenize
from nltk.corpus import stopwords

from analysis.forms import AnalysisForm

class AnalysisView(TemplateView):
    template_name = "analysis/analysis.html"

    def create_frequency_table(self, text_string):

        stopWords = set(stopwords.words("english"))
        words = word_tokenize(text_string)
        ps = PorterStemmer()

        freqTable = dict()
        for word in words:
            word = ps.stem(word)
            if word in stopWords:
                continue
            if word in freqTable:
                freqTable[word] += 1
            else:
                freqTable[word] = 1

        return freqTable

    def score_sentences(self, sentences, freqTable):
        sentenceValue = dict()

        for sentence in sentences:
            word_count_in_sentence = (len(word_tokenize(sentence)))
            for wordValue in freqTable:
                if wordValue in sentence.lower():
                    if sentence[:10] in sentenceValue:
                        sentenceValue[sentence[:10]] += freqTable[wordValue]
                    else:
                        sentenceValue[sentence[:10]] = freqTable[wordValue]

            sentenceValue[sentence[:10]] = sentenceValue[sentence[:10]] // word_count_in_sentence

        return sentenceValue

    def find_average_score(self, sentenceValue):
        sumValues = 0
        for entry in sentenceValue:
            sumValues += sentenceValue[entry]

        # Average value of a sentence from original text
        average = int(sumValues / len(sentenceValue))

        return average

    def generate_summary(self, sentences, sentenceValue, threshold):
        sentence_count = 0
        summary = ''

        for sentence in sentences:
            if sentence[:10] in sentenceValue and sentenceValue[sentence[:10]] > (threshold):
                summary += " " + sentence
                sentence_count += 1

        return summary

    def get(self, request):  # 1 Create the word frequency table
        return render(request, self.template_name)


    def post(self, request):
        form = AnalysisForm(request.POST)
        if form.is_valid():
            article = form.cleaned_data['article']
            freq_table = self.create_frequency_table(article)

            '''
            We already have a sentence tokenizer, so we just need 
            to run the sent_tokenize() method to create the array of sentences.
            '''

            # 2 Tokenize the sentences
            sentences = sent_tokenize(article)

            # 3 Important Algorithm: score the sentences
            sentence_scores = self.score_sentences(sentences, freq_table)

            # 4 Find the threshold
            threshold = self.find_average_score(sentence_scores)

            # 5 Important Algorithm: Generate the summary
            summary = self.generate_summary(sentences, sentence_scores, 1.5 * threshold)

            content = {"summary": summary}

            return render(request, self.template_name, content)

        else:
            form = AnalysisForm()
        return render(request, self.template_name)
