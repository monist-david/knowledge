# coding=utf-8
from nltk.stem import WordNetLemmatizer
from nltk.corpus import words

wordlist = set(words.words())
wordnet_lemmatizer = WordNetLemmatizer()

def max_match(text):
    pos2 = len(text)
    result = ''
    while len(text) > 0:
        word = wordnet_lemmatizer.lemmatize(text[0:pos2])
        if word in wordlist:
            result = result + text[0:pos2] + ' '
            text = text[pos2:]
            pos2 = len(text)
        else:
            pos2 = pos2-1
    return result[0:-1]

string = 'President Trump suspended payments to the World Health Organization — a move Bill Gates called “as dangerous as it sounds” — in a frantic attempt to deflect blame from his own delinquency in acting to protect Americans against the pandemic and his ongoing failure to ramp up testing, which would allow economic reengagement.'
res = ''.join(e for e in string if e.isalnum()).lower()
print(max_match(res))
