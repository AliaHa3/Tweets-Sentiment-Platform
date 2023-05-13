import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords
nltk.download("stopwords")
nltk.download("punkt")

arabic_diacritics = re.compile("""
                             ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)


def normalize_arabic(text):
    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    text = re.sub("ة", "ه", text)
    text = re.sub("گ", "ك", text)
    return text


def remove_diacritics(text):
    text = re.sub(arabic_diacritics, '', text)
    return text


def remove_repeating_char(text):
    return re.sub(r'(.)\1+', r'\1', text)

stop_words_2 = []
with open('resources/list.txt','r',encoding='utf-8') as file:
    stop_words_2 = file.read().split('\n')

def remove_stop_words(text):
    stopwords_list = stopwords.words('arabic')
    stopwords_list.extend(stop_words_2)

    return ' '.join(w.strip() for w in text.split() if w.strip()
                    not in stopwords_list and len(w.strip()) > 1)

def remove_hashtags(text):
    text = re.sub("#[A-Za-z0-9_]+","", text)
    return text


def remove_mentions(text):
    text = re.sub("@[A-Za-z0-9_]+","", text)
    return text

def clean_text(text):
    ## Remove hashtags
    # text = remove_hashtags(text)
    ## Remove user mentions
    text = remove_mentions(text)
    ## Remove punctuations 
    text = re.sub('[%s]' % re.escape("""!"#$%&'()*+,،-./:;<=>؟?@[\]^_`{|}~�«»◄“”"""), ' ', text)
    ## remove extra whitespace
    text = re.sub('\s+', ' ', text)
    ## Remove diacritics
    text = remove_diacritics(text)
    ## repeating_char
    text = remove_repeating_char(text)
    ## Remove numbers
    text = re.sub("\d+", " ", text)
    ## Remove english character
    text = re.sub('[A-Za-z]+',' ',text)
    text = re.sub(r'\\u[A-Za-z0-9\\]+',' ',text)
    ## remove extra whitespace
    text = re.sub('\s+', ' ', text) 
    ## Remove stop words
    text = remove_stop_words(text)
    ## Normalize arabic letters
    text = normalize_arabic(text)
     ## Remove stop words
    text = remove_stop_words(text)
    ## remove extra whitespace
    text = re.sub('\s+', ' ', text)  

    return text


# countries = pd.read_json('countries.json',encoding='utf8')
# names = countries.name.values.tolist()
# clean_text_list = [ clean_text(text) for text in names]
# countries['clean_text'] = clean_text_list
# countries.to_csv('Allcountries.csv',encoding='utf8',index=False)