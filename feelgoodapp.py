#!/usr/bin/env python


"""
10:36 PM sunday 
"""

#import libraries
import argparse, httplib2, json, os, random, sys
from random import randint
from oauth2client import tools, file, client
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging
import shelve
from subprocess import check_output
import urllib,json
import shelve
import uuid

import sqlite3



import flask
from flask import request, Flask, render_template, jsonify, abort, redirect




print "######## FEEL-GOOD OF FACEBOOKAPP.PY ###########"
print "########################################"

# Project id value is retrieved from Google Developer Console
# on which I created a project called info253-feel-good
# and for which I have enabled YouTube API
project_id = 'info253-feel-good'


#create application
app = flask.Flask(__name__)
app.debug = True
 
DEVELOPER_KEY = "AIzaSyAy0U-jD2ZhEZFmWtSweEozwsFX5NJN7x0"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

demo_db = shelve.open("demo_db")



@app.route('/')
def indexProject():
    """
    Landing page of the "feel good" application
    Note: the template feel-good-index.html must be in the folder "template"
    """    
    return flask.render_template('facebook.html')





@app.route("/tastes", methods=['GET'])
def tastes():
    return flask.render_template('usertastes.html')





@app.route("/create", methods=['POST', 'GET'])
def create():
    """
    This POST request saves the tastes of the user, when user answers the questions
    of the form
    """



    """
    --------------------------------------------------------------------------------
    STEP 1: RETRIEVE VALUES FROM FORM
    --------------------------------------------------------------------------------

    """



    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    
    uid = uuid.uuid4()
    userID = uid.hex

    preferences = []

    """
    FOOD for Yelp API
    """

    favFood = request.form.getlist('food')
    foods = []
    for item in favFood:
        item = str(item).replace('u\'','')
        foods.append(item)
    favFood = foods
    print "favFood ", favFood
    demo_db["food"] = favFood



    """
    MUSIC genre for Spotify API
    """
    favMusic = request.form.getlist('music')
    music = []
    for item in favMusic:
        item = str(item).replace('u\'','')
        music.append(item)
    favMusic = music
    print "favMusic ", favMusic
    demo_db["music"] = favMusic


    """
    ANIMAL for Youtube API.
    In Youtube API, search words will be: favorite animal + funny
    """
    favAnimal = request.form.getlist('animal')
    animals = []
    for item in favAnimal:
        item = str(item).replace('u\'','')
        animals.append(item)

    favAnimal = animals + ["funny"]

    print "favAnimal ", favAnimal
    demo_db["animal"] = favAnimal



    

    """
    CURRENTFEELING for GIPHY API
    """
    feeling = request.form.getlist('currentfeeling')
    feelings = []
    for item in feeling:
        item = str(item).replace('u\'','')
        feelings.append(item)
    feeling = feelings
    print "feeling ", feeling
    demo_db["emotion"] = feeling

    










   



    """
    --------------------------------------------------------------------------------
    STEP 2: USEFUL FUNCTIONS TO USE APIs
    --------------------------------------------------------------------------------

    """

    


    def youtube_search(searchterm):
   
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


        search_response = youtube.search().list(q=searchterm, \
            part="id,snippet", \
            maxResults=25\
            ).execute()

        videos = []
        channels = []
        playlists = []

        # to obtain the title of the video
        # use: search_result["snippet"]["title"]

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append((search_result["snippet"]["title"], search_result["id"]["videoId"]))

        # Select a random video in all videos suggested for search tearm
        randomVideoSelection = randint(0,len(videos)-1)

        #just return the Id of the Youtube Video
        return [searchterm, videos[randomVideoSelection][1]]



    
    def searchGifOnGiphy(*args):
        """ 
        input: search terms, example: "cats", "dogs"
        ouput: gif url
        """ 
        urlrequest = "http://api.giphy.com/v1/gifs/search?q="
        tot = len(args)
        i = 0
        for ar in args:
            i = i + 1
            if i<len(args):
                urlrequest = urlrequest + ar + "+"
            else:
                i = urlrequest = urlrequest + ar
        data = json.loads(urllib.urlopen(urlrequest + "&api_key=dc6zaTOxFJmzC").read())

        for key, value in data.items():
            if key == "data":
                gifurl = value[randint(0,len(value)-1)]['images']['original']['url']
        return gifurl



    """
    --------------------------------------------------------------------------------
    STEP 3: RETURN RANDOM PAGE
    --------------------------------------------------------------------------------

    """

    firstPageNumber = random.randint(0, 1)
    
   

    if firstPageNumber == 0:
        """
        Show ANIMAL with Youtube API
        """
        
        return flask.render_template('feel-good-animal.html', youtubeId = youtube_search(demo_db['animal'])[1], favAni = youtube_search(demo_db['animal'])[0])

    if firstPageNumber ==1:

        return flask.render_template('feel-good-gif.html', gifurl = searchGifOnGiphy(demo_db['animal'][0]))


    if firstPageNumber == 2:

        return flask.render_template('feel-good-quote.html', gifurl = searchGifOnGiphy(demo_db['animal'][0]))








@app.route("/create2", methods=['POST','GET'])
def create2():

    """
    --------------------------------------------------------------------------------
    RE-GENERATE RANDOM PAGES
    --------------------------------------------------------------------------------

    """

    print "the second time  ", demo_db['animal']


    def youtube_search(searchterm):
   
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


        search_response = youtube.search().list(q=searchterm, \
            part="id,snippet", \
            maxResults=25\
            ).execute()

        videos = []
        channels = []
        playlists = []

        # to obtain the title of the video
        # use: search_result["snippet"]["title"]

        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                videos.append((search_result["snippet"]["title"], search_result["id"]["videoId"]))

        # Select a random video in all videos suggested for search tearm
        randomVideoSelection = randint(0,len(videos)-1)

        #just return the Id of the Youtube Video
        return [searchterm, videos[randomVideoSelection][1]]

    
    return flask.render_template('feel-good-animal.html', youtubeId = youtube_search(demo_db['animal'])[1])



if __name__ == "__main__":
    app.run()
