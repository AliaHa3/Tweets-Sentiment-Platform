from app.base.models import Lexicon
import pandas as pd
import numpy as np
from collections import Counter
import re
import time
from flashtext import KeywordProcessor
import datetime

from .preprocess import *
from .gender_detection import detect_gender,transString
from app.base.models import db,Lexicon,ConfigsTable
from app.base.routes import changes_in_lexicon

countries = pd.read_csv('resources/Allcountries.csv',encoding='utf8')

def setup_countries_keywords(countries):
    countries_keyword_processor = KeywordProcessor()
    for index,country in countries.iterrows():
        countries_keyword_processor.add_keyword(country.clean_text,country.code)
    arabic_chars ='ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
    for char in arabic_chars:
        countries_keyword_processor.add_non_word_boundary(char)
    return countries_keyword_processor

countries_keyword_processor = setup_countries_keywords(countries)


def setup_sentiment_keywords():
    sentiment_keyword_processor = KeywordProcessor()

    pos = db.session.query(Lexicon).filter_by(sentiment='pos').all()
    pos = [obj.clean_word for obj in pos]

    neg = db.session.query(Lexicon).filter_by(sentiment='neg').all()
    neg = [obj.clean_word for obj in neg]

    for word in pos:
        if  type(word) != float:
            sentiment_keyword_processor.add_keyword(word,'pos')

    for word in neg:
        if type(word) != float:
            sentiment_keyword_processor.add_keyword(word,'neg')

    arabic_chars ='ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
    for char in arabic_chars:
        sentiment_keyword_processor.add_non_word_boundary(char)
    return sentiment_keyword_processor

sentiment_keyword_processor = setup_sentiment_keywords()


def total_tweet_count(tweets):
    total_tweet_count = len(tweets)
    return total_tweet_count

def total_retweet_count(tweets):
    total_retweet_count = tweets.retweets_count.sum()
    return total_retweet_count

def total_likes_count(tweets):
    total_likes_count = tweets.likes_count.sum()
    return total_likes_count

def total_tweets_per_hour(tweets):
    hours = [0] * 24
    existed_hour = tweets.groupby(['hour']).count().index.values.tolist()
    tweets_per_hour = tweets.groupby(['hour']).count()['id'].values.tolist()
    for i,hour in enumerate(existed_hour):
        hours[hour] = tweets_per_hour[i]

    return hours

def total_retweets_per_hour(tweets):
    hours = [0] * 24
    existed_hour = tweets.groupby(['hour']).count().index.values.tolist()
    tweets_per_hour = tweets.groupby(['hour'])['retweets_count'].sum().values.tolist()
    for i,hour in enumerate(existed_hour):
        hours[hour] = tweets_per_hour[i]

    return hours

def total_likes_per_hour(tweets):
    hours = [0] * 24
    existed_hour = tweets.groupby(['hour']).count().index.values.tolist()
    tweets_per_hour = tweets.groupby(['hour'])['likes_count'].sum().values.tolist()
    for i,hour in enumerate(existed_hour):
        hours[hour] = tweets_per_hour[i]

    return hours

def to_12hour_format(hour):
    if hour == 0:
        hour = f"12:00AM"
    elif hour < 12:
        hour = f"{hour}:00AM"
    else:
        hour = f"{hour-12}:00PM"
    return hour

def lowest_active_hour(total_actions_per_hour):
    lowest_hour = total_actions_per_hour.index(min(total_actions_per_hour))
    lowest_hour = f"{to_12hour_format(lowest_hour)}-{to_12hour_format(lowest_hour+1)}"
    return lowest_hour

def highest_active_hour(total_actions_per_hour):
    highest_hour = total_actions_per_hour.index(max(total_actions_per_hour))
    highest_hour = f"{to_12hour_format(highest_hour)}-{to_12hour_format(highest_hour+1)}"
    return highest_hour

def most_retweet_tweet(tweets):
    link = tweets.iloc[tweets.retweets_count.idxmax()].link
    return link

def most_liked_tweet(tweets):
    link = tweets.iloc[tweets.likes_count.idxmax()].link
    return link

def most_active_tweet(tweets):
    link = tweets.iloc[tweets.actions.idxmax()].link
    return link

def top_hashtags(tweets,top_n=10):
    hashtags_list = tweets.hashtags.values.tolist()
    hashtags = [tag for l in hashtags_list for tag in eval(str(l))]
    counts = Counter(hashtags)
    top_hashtags = counts.most_common(top_n)
    total_hashtags = sum(list(counts.values()))
    return top_hashtags,total_hashtags

def extract_mentions(tweet):
    mentions = re.findall("@([a-zA-Z0-9_]{1,50})", tweet)
    return mentions

def top_mentions(tweets,top_n=10):
    tweets = tweets.tweet.values.tolist()
    mentions = [mention for tweet in tweets for mention in extract_mentions(tweet)]
    counts = Counter(mentions)
    top_mentions = counts.most_common(top_n)
    total_mentions = sum(list(counts.values()))
    return top_mentions,total_mentions

def top_keywords(clean_tokens,top_n=10):
    counts = Counter(clean_tokens)
    counts = counts.most_common(25)
    top_words = counts.most_common(top_n)
    total_words = sum(list(counts.values()))
    return top_words,total_words

def top_countries_mentions(tweets,countries,countries_keyword_processor=countries_keyword_processor,top_n=10):    
    all_tweets_text = ' '.join([text for text in tweets.clean_tweets])
    keywords_found = countries_keyword_processor.extract_keywords(all_tweets_text)
    counts = Counter(keywords_found)
    top_countries = counts.most_common(10)
    top_countries = [(item[0],countries[countries['code'] == item[0]].iloc[0]['name'],item[1])
                    for item in top_countries]
    total_countries_count = sum(list(counts.values()))
    return top_countries,total_countries_count

def sentiment_analysis(tweets):
    sentiment_list = tweets.sentiment.values.tolist()
    counts = Counter(sentiment_list)
    return dict(counts)

def analyse_sources(tweets):
    source_list = tweets.source.values.tolist()
    counts = Counter(source_list)

    return dict(counts)

def analyse_genders(tweets):
    usernames = tweets.username.values.tolist()
    screennames = tweets.name.values.tolist()
    genders = []
    for user_name,screen_name in zip(usernames,screennames):
        gender1a = detect_gender(user_name)
        gender2a = detect_gender(screen_name)

        user_name = transString(user_name, reverse=0).lower()
        screen_name = transString(screen_name, reverse=0).lower()

        gender1b = detect_gender(user_name)
        gender2b = detect_gender(screen_name)
        name_gender = [gender1a,gender1b,gender2a,gender2b]
        

        if 'female'in name_gender:
            genders.append('female')
        elif 'male' in name_gender:
            genders.append('male')
        else:
            genders.append('unknown')
    
    counts = Counter(genders)
    return dict(counts)


def generate_report(tweets):

    report = {  'total_tweet': total_tweet_count(tweets),
                'total_retweet': total_retweet_count(tweets),
                'total_likes' : total_likes_count(tweets),
                
                'total_tweets_per_hour' : total_tweets_per_hour(tweets),
                'total_retweets_per_hour' : total_retweets_per_hour(tweets),
                'total_likes_per_hour' : total_likes_per_hour(tweets),

                'most_liked_tweet' : most_liked_tweet(tweets),
                'most_retweet_tweet' : most_retweet_tweet(tweets),
                'most_active_tweet' : most_active_tweet(tweets)

            }

    report['total_published'] = report['total_tweet'] + report['total_retweet']
    report['total_actions'] = report['total_published'] + report['total_likes']
    report['total_published_per_hour'] = list ( np.array(report['total_tweets_per_hour']) +
                                                np.array(report['total_retweets_per_hour']))
    report['total_actions_per_hour'] = list ( np.array(report['total_published_per_hour']) +
                                                np.array(report['total_likes_per_hour']))


    report['lowest_active_hour'] = lowest_active_hour(report['total_actions_per_hour'])
    report['highest_active_hour'] = highest_active_hour(report['total_actions_per_hour'])

    report['top_hashtags'], report['total_hashtags_count'] = top_hashtags(tweets,top_n=10)
    report['top_mentions'], report['total_mention_count'] = top_mentions(tweets,top_n=10)
    report['top_countries_mentions'], report['top_countries_mentions_count'] = top_countries_mentions(tweets,countries,countries_keyword_processor,top_n=10)
    
    report['analyse_sentiments'] = sentiment_analysis(tweets)
    report['analyse_sources'] = analyse_sources(tweets)
    report['analyse_genders'] = analyse_genders(tweets)

    return report


def convert_to_hour(time_text):
    return datetime.datetime.strptime(time_text, '%H:%M:%S').time().hour


def sentiment_extraction(tweet):    
    keywords_found = sentiment_keyword_processor.extract_keywords(tweet)
    counts = Counter(keywords_found)
    count_pos = counts['pos']
    count_neg = counts['neg']
    total_count = count_pos - count_neg
    sentiment = 'neutral'
    sentiment = 'pos' if total_count >= 1 else sentiment
    sentiment = 'neg' if total_count <= -1 else sentiment
    return sentiment

def process_tweets_data(path):
    global changes_in_lexicon,sentiment_keyword_processor

    if changes_in_lexicon:
        sentiment_keyword_processor = setup_sentiment_keywords()
        changes_in_lexicon = False

    tweets = pd.read_csv(path,encoding='utf8')
    tweets['actions'] = np.array(tweets.likes_count) + np.array(tweets.retweets_count)
    tweets['clean_tweets'] = tweets.tweet.apply(lambda x: clean_text(x))
    tweets['hour'] = tweets.time.apply(lambda x: convert_to_hour(x))
    tweets['sentiment'] = tweets.clean_tweets.apply(lambda x: sentiment_extraction(x))
    clean_tokens = tweets.clean_tweets.apply(lambda x: x.split())
    clean_tokens = [token for token_list in clean_tokens for token in token_list]
    

    return tweets,clean_tokens


def process_tweets_data_df(tweets):
    global changes_in_lexicon,sentiment_keyword_processor,lexicon

    default_config = db.session.query(ConfigsTable).filter_by(name='changes_in_lexicon').first()
 
    if default_config.value == 'True':
        print("New Changes in Lexicon")
        sentiment_keyword_processor = setup_sentiment_keywords()
        default_config.value = 'False'
        db.session.add(default_config)
        changes_in_lexicon = False

    tweets['actions'] = np.array(tweets.likes_count) + np.array(tweets.retweets_count)
    tweets['clean_tweets'] = tweets.tweet.apply(lambda x: clean_text(x))
    tweets['hour'] = tweets.time.apply(lambda x: convert_to_hour(x))
    tweets['sentiment'] = tweets.clean_tweets.apply(lambda x: sentiment_extraction(x))
    clean_tokens = tweets.clean_tweets.apply(lambda x: x.split())
    clean_tokens = [token for token_list in clean_tokens for token in token_list]
    

    return tweets,clean_tokens