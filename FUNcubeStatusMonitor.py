# Python script to monitor FUNcube-1 status and update the 
# @FUNcubeUK Twitter account on changes

import os
import re
import json
import urllib.request as urllib2
from pprint import pprint
from sys import exit
import tweepy
from dotenv import load_dotenv

# Load consumer keys and access tokens from .env, used for OAuth
load_dotenv(dotenv_path='.env')

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(os.getenv("CONSUMER_KEY"), os.getenv("CONSUMER_SECRET"))
auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_TOKEN_SECRET"))
 
# Creation of the actual interface, using authentication
api = tweepy.API(auth)
 
user = api.me()
 
print('Name: ' + user.name)
print('Location: ' + user.location)
print('Followers: ' + str(user.followers_count))

url = "http://warehouse.funcube.org.uk/ui/realtime/2.json"

try:
    jsonurl = urllib2.urlopen(url)
except urllib2.HTTPError as err:
    if err.code == 404:
        print("404 not found")
    else:
        print("Unknown error. Error code:", err.code)
        print(err.read())
    exit(0)

text = json.loads(jsonurl.read())
pprint(text)

SatMode = text["satelliteMode"].upper()
TransponderState = text["transponderState"].upper()

print("Satellite Mode: ", SatMode)
print("Transponder State:", TransponderState)

recent_tweets = api.user_timeline()

for recent_tweet in recent_tweets:
    if recent_tweet.text.find("FUNcube-1 status update") == 0:
        # The tweet was a status update, stop searching recent tweets
        print("Most recent status update tweet: ", recent_tweet.text)

        matchObj = re.match(".*Mode (\w+). Transponder (\w+).", recent_tweet.text)

        if matchObj:
            PreviousSatMode = matchObj.group(1)
            PreviousTransponderState = matchObj.group(2)
        else:
            print ("No match!")
            exit(0)
        break
else:
    # Didn't find a tweet that was a status update
    exit(0)

print("Previous Satellite Mode: ", PreviousSatMode)
print("Previous Transponder Mode: ", PreviousTransponderState)

if SatMode == PreviousSatMode and TransponderState == PreviousTransponderState:
   #If neither switching mode or transponder state have changed do nothing
   print('Satellite status unchanged - NOP')
elif SatMode == "Auto" and PreviousSatMode == "Auto":
   #If in automatic mode and transponder state changes, do nothing
   print('Transponder state changed in auto mode - NOP')
else:
   print('Switching mode change or change of transponder state whilst in manual mode - UPDATING @FUNCUBEUK STATUS')
   
   if SatMode == 'Auto':
         SatModeDesc = 'AUTO'
   else: 
        SatModeDesc = 'MANUAL'
  
   if TransponderState == 'Off':
         TransponderStateDesc = 'OFF'
   else:
         TransponderStateDesc = 'ON'

   tweetText = 'FUNcube-1 status update: Mode ' + SatModeDesc + '. Transponder ' +  TransponderStateDesc + '. #FUNcube #amsat #hamradio'
   print(tweetText)
   api.update_status(tweetText)