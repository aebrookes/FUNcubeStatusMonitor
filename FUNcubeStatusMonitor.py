# Python script to monitor FUNcube-1 status and update the 
# @FUNcubeUK Twitter account on changes

import os
import csv
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

SatMode = text["satelliteMode"]
TransponderState = text["transponderState"]

print("Satellite Mode: ", SatMode)
print("Transponder State:", TransponderState)

line_number = 0
with open('FUNcubeStatus.csv', 'r') as f:
    mycsv = csv.reader(f)
    mycsv = list(mycsv)
    PreviousTransponderState = mycsv[line_number][1]
    PreviousSatMode  = mycsv[line_number][0]

with open('FUNcubeStatus.csv', 'w') as fp:
    a = csv.writer(fp, delimiter=',')
    data = [[text["satelliteMode"], text["transponderState"]]]
    a.writerows(data)

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