# %pip install gender-guesser
import gender_guesser.detector as gender
# %pip install unidecode
from unidecode import unidecode 
# from mtranslate import translate
import os
import pickle
import re
import pandas as pd
from flashtext import KeywordProcessor
from collections import Counter
from app.base.models import db,Names,ConfigsTable
from app.base.routes import changes_in_names_lexicon

if os.path.exists("resources/detector.pickle"):
    detector = pickle.load(open("resources/detector.pickle", "rb"))
else:
    detector = gender.Detector(case_sensitive=False)
    with open("resources/detector.pickle", "wb+") as f:
        pickle.dump(detector, f)

import pickle
filename = 'resources/names_model.sav'
loaded_names_model = pickle.load(open(filename, 'rb'))


def setup_names_keywords():
    names_keyword_processor = KeywordProcessor()
    
    males = db.session.query(Names).filter_by(gender='ذكر').all()
    males = [obj.name for obj in males]

    females = db.session.query(Names).filter_by(gender='انثى').all()
    females = [obj.name for obj in females]

    for word in males:
        if  type(word) != float:
            names_keyword_processor.add_keyword(word,'male')

    for word in females:
        if type(word) != float:
            names_keyword_processor.add_keyword(word,'female')

    arabic_chars ='ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
    for char in arabic_chars:
        names_keyword_processor.add_non_word_boundary(char)
    return names_keyword_processor

names_keyword_processor = setup_names_keywords()


def split(s):
    try:
        return s.split()[0]
    except IndexError:
        return s


def rm_punctuation(s, _pat=re.compile(r"\W+")):
    return _pat.sub(" ", s)


buck2uni = {"'": u"\u0621", # hamza-on-the-line
            "|": u"\u0622", # madda
            ">": u"\u0623", # hamza-on-'alif
            "&": u"\u0624", # hamza-on-waaw
            "<": u"\u0625", # hamza-under-'alif
            "}": u"\u0626", # hamza-on-yaa'
            "A": u"\u0627", # bare 'alif
            "b": u"\u0628", # baa'
            "p": u"\u0629", # taa' marbuuTa
            "t": u"\u062A", # taa'
            "v": u"\u062B", # thaa'
            "j": u"\u062C", # jiim
            "H": u"\u062D", # Haa'
            "x": u"\u062E", # khaa'
            "d": u"\u062F", # daal
            "*": u"\u0630", # dhaal
            "r": u"\u0631", # raa'
            "z": u"\u0632", # zaay
            "s": u"\u0633", # siin
            "$": u"\u0634", # shiin
            "S": u"\u0635", # Saad
            "D": u"\u0636", # Daad
            "T": u"\u0637", # Taa'
            "Z": u"\u0638", # Zaa' (DHaa')
            "E": u"\u0639", # cayn
            "g": u"\u063A", # ghayn
            "_": u"\u0640", # taTwiil
            "f": u"\u0641", # faa'
            "q": u"\u0642", # qaaf
            "k": u"\u0643", # kaaf
            "l": u"\u0644", # laam
            "m": u"\u0645", # miim
            "n": u"\u0646", # nuun
            "h": u"\u0647", # haa'
            "w": u"\u0648", # waaw
            "Y": u"\u0649", # 'alif maqSuura
            "y": u"\u064A", # yaa'
            "F": u"\u064B", # fatHatayn
            "N": u"\u064C", # Dammatayn
            "K": u"\u064D", # kasratayn
            "a": u"\u064E", # fatHa
            "u": u"\u064F", # Damma
            "i": u"\u0650", # kasra
            "~": u"\u0651", # shaddah
            "o": u"\u0652", # sukuun
            "`": u"\u0670", # dagger 'alif
            "{": u"\u0671", # waSla
}


#predict the gender of an arabic name
def predict(model,name):
    try:
        letter_dict={'ا':1,'ب':2,'ت':3,'ث':4,'ج':5,'ح':6,'خ':7,'د':8,'ذ':9,'ر':10,'ز':11,'س':12,'ش':13,'ص':14,'ض':15,'ط':16,'ظ':17,'ع':18,'غ':19,'ف':20,'ق':21,'ك':22,'ل':23,'م':24,'ن':25,'ه':29,'و':27,'ؤ':27,'ي':28,'ء':30,'ئ':28,'-':0,'أ':1,'ة':29,'،':0,'\u200f':0,'.':0,'\t':0,'ى':28}
        if (len(name)>2):
            third_letter=name[-3]
        else:
            third_letter="-"
        if (model.predict([[letter_dict[name[-1]],letter_dict[name[-2]],letter_dict[third_letter],0,0]])):
            return "male"
        else:
            return "female"    
    except:
        return 'unknown'
    

def transString(string, reverse=0):
    '''Given a Unicode string, transliterate into Buckwalter. To go from
    Buckwalter back to Unicode, set reverse=1'''

    for k, v in buck2uni.items():
        if not reverse:
            string = string.replace(v, k)
        else:
            string = string.replace(k, v)

        string = string.replace("E","a")
    return string

def genders_extraction(user_name):
    global changes_in_names_lexicon,names_keyword_processor

    default_config = db.session.query(ConfigsTable).filter_by(name='changes_in_names').first()


    if default_config.value == 'True':
        print("New Changes in Names")
        names_keyword_processor = setup_names_keywords()
        changes_in_names_lexicon = False
        default_config.value = 'False'
        db.session.add(default_config)

    try:
        keywords_found = names_keyword_processor.extract_keywords(user_name)
        counts = Counter(keywords_found)
        counts = dict(counts)

        if 'female' in counts:
            return 'female'
        elif 'male' in counts:
            return 'male'
        else:
            return 'unknown'
    except:
        return 'unknown' 
    

def detect_gender(user_name):
    for name in [
            (split(user_name)),
            (user_name),
            (split(unidecode(user_name))),
            (unidecode(user_name)),
            (rm_punctuation(user_name))]:

                g = detector.get_gender(name)

                if g == 'andy':
                    g = "unknown"

                if g.startswith("mostly_"):
                    g = g.split("mostly_")[1]

                if g != "unknown":
                    # Not androgynous.
                    break

                g = genders_extraction(name)

                if g != "unknown":
                    # Not androgynous.
                    break

                g = predict(loaded_names_model,name)

                if g != "unknown":
                    # Not androgynous.
                    break
                
    return g

