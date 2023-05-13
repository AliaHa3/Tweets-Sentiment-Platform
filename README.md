# Tweets-Sentiment-Platform
Lexicon Arabic Tweets Sentiment Platform based on Hashtag (Responsive Wep Application)

[Web Demo](https://youtu.be/cAqKSIp-f1U)
[Mobile Demo](https://youtu.be/ptvAxVro_Lc)

## Project Goal
The project aims to search for tweets based on the following data:
* A word or hashtag.
* Date of a specific day.
* Location of tweets (optional)
It fetches tweets from Twitter first, then analyzes them, and then sends an alert email when the analysis is completed.

## Project Insights
1. The total number of tweets during the selected day, not including retweets.
2. The number of times the tweets were retweeted during the selected day.
3. The number of times a Tweet was hit like during the selected day.
4. The number of posts on the topic: the number of tweets and retweets during the selected day.
5. Number of Interactors: The total number of interactions with the topic during the day, including retweets, retweets, and likes.
6. Statistics of tweets according to the selected day.
7. The highest period in which the topic is published and interacted with during the day.
8. The least period during which the topic is published and interacted with during the day.
9. Most used tags.
10. The most mentioned users in tweets.
11. The most visible countries in the texts of tweets.
12. Most Engaged Tweet Overall Today.
13. Most liked tweet of the day.
14. Most retweeted tweet of the day.
15. Predict the gender of the tweet by classifying the username.
16. An indicator of the direction of the whole tweets (negative or positive) by categorizing the tweets (negative-positive-neutral).

## Project Web Pages
* **Guest**: has two web pages
    * The main page to enter the id of the search process and to show all the analyzes in an interactive way and illustrations
    * Report creation page: In it, the requirements for the search to be conducted are entered
* **Admin**: has access to the regular user pages as well as the following pages:
    * Change password page.
    * New admin registration page.
    * A page for browsing, searching, and deleting words used to classify tweets according to their feelings (The number of words in the database is currently 13,120).
    * A page for browsing, searching, and deleting words used to classify the gender of tweeters by name (The number of names currently in the database is 6,348).
Default Admin account (Username : admin, Password: 123456)

**Note:**
For the testing process, Google Gmail was approved, but its free service provides only 100 emails per month, so you must adopt a paid version of it or rely on your own mail server


## Project Structure:
1.	Resources folder: contain resources files like names of countries in world, machine learning model to classify names, list of words.
2.	Config.py file: contain the configurations of application
3.	App folder:
	* Home folder: contain the pages, models and code for Normal users
    * Base folder: contain the pages, models and codes for Admin users

## How to run the project:
1.	Open terminal and run the followings:
	```
    sudo apt-get install rabbitmq-server
	sudo rabbitmq-server -detached
    ```
2.	Open another terminal and change current directory to the directory inside the project code

3.	Run the following command:
```pip3 install --user --upgrade git+https://github.com/himanshudabas/twint.git@origin/twint-fixes#egg=twint ```

4.	Then Run the following command:
```Pip install –r requirements.txt```

5.	Open config.py and change the following parameters:

(the parameters of email and ip server of deployment server)

6. run the following commands:
```
nohup gunicorn --bind 0.0.0.0:5003 run:app > server.log 2>&1 & echo $! > server_pid.txt

nohup celery -A celery_worker:celery worker  --loglevel=info > workers.log 2>&1 & echo $! > workers_pid.txt
```
7. to stop the application run the following:
```
kill -9 `cat server_pid.txt`
rm server_pid.txt

kill -9 `cat workers_pid.txt`
rm workers_pid.txt
```
