

#pip3 install --user --upgrade git+https://github.com/himanshudabas/twint.git@origin/twint-fixes#egg=twint

import twint
import time
from .worldcountries import *
import pandas as pd
import numpy as np
from .preprocess import *
from .utils import *

sources = ['Twitter Web Client','Twitter Web App','Twitter for Android','Twitter for iPhone']


# for country,country_names in alpha2countries_dict.items():
#     for country_name in country_names:
#         c = twint.Config()
#         c.Limit = 100
#         c.Search = "رمضان"
#         c.Pandas = True
#         c.Lang = "ar"
#         c.Since = "2021-04-01"
#         c.Until = "2021-05-11"
#         c.Near = country_name
#         c.Popular_tweets = True
#         c.Source = sources[0]
#         twint.run.Search(c)
        
#         Tweets_df = twint.storage.panda.Tweets_df
#         Tweets_df['near'] = country

#         Tweets_dfs_list.append(Tweets_df)

#         time.sleep(10)

#         print(time.time() - start)


# print(time.time() - start)

# print(Tweets_df)

def search_tweets(out_file,query,since_date,until_date,limit_tweet_count=None,country_name=None):
    Tweets_dfs_list = []
    start = time.time()
    if limit_tweet_count is not None:
        limit = int(limit_tweet_count/len(sources))
    for source in sources:
        c = twint.Config()
        
        if limit_tweet_count is not None:
            c.Limit = limit

        if country_name is not None:
            c.Near = country_name
        
        c.Search = query
        c.Pandas = True
        c.Lang = "ar"
        c.Since = since_date
        c.Until = until_date
        
        c.Popular_tweets = True
        c.Source = source
        twint.run.Search(c)
        
        Tweets_df = twint.storage.panda.Tweets_df
        # Tweets_df['near'] = country

        Tweets_dfs_list.append(Tweets_df)

        time.sleep(15)
        
    Tweets_df = pd.concat(Tweets_dfs_list)
    # Tweets_df.to_csv(f'{out_file}.csv',encoding ='utf-8',index=False)

    return Tweets_df

def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()

def analyse_query(out_file,query,since_date,until_date,limit_tweet_count,country_name):
    start = time.time()

    print("start fetching ....")
    Tweets_df = search_tweets(out_file,query,since_date,until_date,limit_tweet_count,country_name)
    print("end fetching ....")

    Tweets_df.dropna(how='all',inplace=True)
    
    print("start analysing ....")
    tweets,clean_tokens = process_tweets_data_df(Tweets_df)
    report = generate_report(tweets)
    print(time.time() - start)
    print("end analysing ....")

    return report
    
