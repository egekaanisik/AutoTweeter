import tweepy
import re
import json
from pathlib import Path
import os
import schedule
from datetime import datetime
from time import sleep

PATH = Path(__file__).parent.joinpath("config.json")

def main():
    global config
    global api
    global count

    log("Starting bot...")
    config = get_config()
    api = get_api()
    log("Logged in!")
    count = get_day_count()
    log("Current day count: {}".format(count))

    schedule.every().day.at(config["scheduled_time"]).do(tweet)
    log("Scheduled the tweets to be sent at {}.".format(config["scheduled_time"]))

    log("Waiting for the next trigger...")
    while True:
        schedule.run_pending()
        sleep(15)

def get_config():
    if not os.path.exists(PATH):
        reset_config_file(FileNotFoundError, "Config not found. Created a new one. Fill the necessary values and run the script again.")

    with open(PATH, "r", encoding="utf8") as file: config = dict(json.loads("".join(file.readlines())))

    keys = ["api_key", "api_secret", "access_key", "access_secret", "tweet_content", "scheduled_time"]

    if set(config.keys()) != set(keys):
        reset_config_file(ValueError, "Invalid JSON keys. Recreated the config file. Fill the necessary values and run the script again.")

    return config

def reset_config_file(ex_type, ex):
    with open(PATH, "w") as file: file.write(json.dumps({"api_key":"","api_secret":"","access_key":"","access_secret":"","tweet_content":"","scheduled_time":""}))
    raise ex_type(ex)

def get_api():
    global config

    auth = tweepy.OAuthHandler(config["api_key"], config["api_secret"])
    auth.set_access_token(config["access_key"], config["access_secret"])
    api = tweepy.API(auth)
    return api

def get_day_count():
    global api

    tweets_list = api.user_timeline(count=1)
    
    if tweets_list == None or tweets_list == []:
        return 1
    
    tweet = tweets_list[0]
    match = re.search("([0-9]+)\.", tweet.text)

    if match  == None:
        return 1
    else:
        return int(match.group(1))+1

def tweet():
    global config
    global api
    global count

    log("Sending tweet of day #{}...".format(count))
    tweet = config["tweet_content"].format(count)
    api.update_status(tweet)
    log("Sent!")
    log("Waiting for the next trigger...")
    count += 1

def log(msg):
    print("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] " + msg)

if __name__ == "__main__":
    main()