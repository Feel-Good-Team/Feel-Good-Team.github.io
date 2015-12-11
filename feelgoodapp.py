#!/usr/bin/env python

#import libraries
import argparse, httplib2, json, os, random, sys
from random import randint
from oauth2client import tools, file, client
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import logging
import shelve
from subprocess import check_output
import urllib,json
import shelve
import uuid
import requests
import base64
import pprint


from os import environ
import hashlib
import string
import random


# Libraries for QUOTE database:
from xlrd import open_workbook
import sqlite3
from sqlite3 import OperationalError
import time
import datetime

#Yelp 
import argparse
import json
import pprint
import sys
import urllib
import urllib2
import random 

import oauth2


# Libraries for flask
import flask
from flask import request, Flask, render_template, jsonify, abort, redirect, make_response, g




print "######## FEEL-GOOD OF FACEBOOKAPP.PY ###########"
print "########################################"

# Project id value is retrieved from Google Developer Console
# on which I created a project called info253-feel-good
# and for which I have enabled YouTube API
project_id = 'info253-feel-good'


#################################################################
#                   CREATE APPLICATION                          #
################################################################# 
app = flask.Flask(__name__)
app.debug = True


#################################################################
#                            YOUTUBE                            #
################################################################# 
DEVELOPER_KEY = "AIzaSyAy0U-jD2ZhEZFmWtSweEozwsFX5NJN7x0"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"



#################################################################
#                            SPOTIFY                            #
#################################################################
#  Client Keys
CLIENT_ID = "c527924557d747fc86cca93e505f297c"
CLIENT_SECRET = "0cc62b7574e54f7f87f8321f7e3b569a"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://localhost"
PORT = 5000
REDIRECT_URI = "{}:{}/callback".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}



#################################################################
#                              YELP                             #
#################################################################

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 10
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'


CONSUMER_KEY   = "mDAEyzxc5Hj-Dn6db5dW1A"
CONSUMER_SECRET  = 'fhLeyV2pGjjVXYV5gNGTa9N4PB8'
TOKEN           = '9DWp6zTn5yquHlXMo_VupVajnTtLl8Zg'
TOKEN_SECRET    = 'hO0SEzRJAMUg_k0bLn0IryI0sGQ'






################################################################

#storing values of the form
demo_db = shelve.open("demo_db")

# Database/Dictionary to save shortened URLs
db = shelve.open("shorten.db")

#database of user's level of happiness
happy_db = shelve.open("happy_db")


@app.route('/')
def indexProject():
    """
    Landing page of the "feel good" application
    Note: the template feel-good-index.html must be in the folder "template"
    """



    def tableCreate():
        conn = sqlite3.connect('motiveQuote.db')
        c = conn.cursor()
        try:
            c.execute("CREATE TABLE stuffToPlot(ID INT, quote TEXT, author TEXT, majortheme TEXT, minortheme TEXT)")
        except OperationalError:
            None

    def enterData():
        """
        Open Excel file named simple.xlsx where all quotes are.
        """
        conn = sqlite3.connect('motiveQuote.db')
        c = conn.cursor()

        book = open_workbook('simple.xlsx',on_demand=True)
        sheet = book.sheet_by_name("Sheet1")

        # Number of columns
        num_cols = sheet.ncols
        # Number of rows
        nrows = sheet.nrows
        # rowId for DB will be integers 0, 1, 2, etc.
        idForDb = -1

        # Iterate through rows
        for row_idx in range(0, sheet.nrows):
            # Get cell object (quote) by row, col
            cell_obj_quote = sheet.cell(row_idx, 0)  
            quote = cell_obj_quote.value
            
            cell_obj_author = sheet.cell(row_idx, 1)
            author = cell_obj_author.value
            
            cell_obj_maj = sheet.cell(row_idx, 2)
            majortheme = cell_obj_maj.value
            
            cell_obj_min = sheet.cell(row_idx, 3)
            minortheme = cell_obj_min.value
            
            idForDb = idForDb + 1

            c.execute("INSERT INTO stuffToPlot (ID, quote, author, majortheme, minortheme) VALUES (?,?,?,?,?)", 
                (idForDb, quote, author, majortheme, minortheme))

            conn.commit()  

        
    tableCreate()

    enterData()


    return flask.render_template('facebook.html')



"""
GO TO FORM
"""

@app.route("/tastes", methods=['GET', 'POST'])
def tastes():
    #userFacebookId = str(request.form["myField"])
    userMood = request.form['myMood']
    userMood = round(float(userMood),1)
    happy_db['currentuser'] = userMood
    return flask.render_template('usertastes.html')



@app.route("/logout", methods=['GET'])
def logout():

    return flask.render_template('exit.html',levelOfHappiness = happy_db['currentuser'] )



@app.route("/create", methods=['POST', 'GET'])
def create():
    """
    User press submit button with "POST" method from usertastes.html
    Step 1: save the values from the form in a DB
    Step 2: generate the pages
    """

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    """
    --------------------------------------------------------------------------------
    STEP 1: RETRIEVE VALUES FROM FORM
    DON'T FORGET TO CLEAN DB
    --------------------------------------------------------------------------------

    """

    if request.method == 'POST':

        """
        FOOD for Yelp API
        """
        favFood = request.form.getlist('food')
        foods = []
        for item in favFood:
            item = str(item).replace('u\'','')
            foods.append(item)
        favFood = foods
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
        demo_db["music"] = favMusic

        """
        ANIMAL for Youtube API.
        In Youtube API, search words will be: favorite animal + funny
        """
        favAnimal = request.form.getlist('pets')
        animals = []
        for item in favAnimal:
            item = str(item).replace('u\'','')
            animals.append(item)

        favAnimal = animals + ["cute", "animals"]

        demo_db["pets"] = favAnimal


        """
        CURRENTFEELING for GIPHY API
        """
        feeling = request.form.getlist('gifs')
        feelings = []
        for item in feeling:
            item = str(item).replace('u\'','')
            feelings.append(item)
        feeling = feelings
        demo_db["gifs"] = feeling[0]

        return redirect('/create')


    if request.method == 'GET':


        def youtube_search(searchterm):
            """
            input: music genre
            output: [input, youtubeVideoId]
            """
       
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)


            search_response = youtube.search().list(q=searchterm, \
                part="id,snippet", \
                maxResults=40\
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
            total = len(args)
            randomNumber = random.randint(0, total-1)
            searchgif = args[randomNumber]

            #generate the URL for the giphy API
            urlrequest = "http://api.giphy.com/v1/gifs/search?q="
            urlrequest = urlrequest + searchgif

            data = json.loads(urllib.urlopen(urlrequest + "&api_key=dc6zaTOxFJmzC").read())

            for key, value in data.items():
                if key == "data":
                    gifurl = value[randint(0,len(value)-1)]['images']['original']['url']
            return gifurl

        
        def spot(*args):
            total = len(args)
            randomNumber = random.randint(0, total-1)
            searchgenre = args[randomNumber][0]
            urlrequest = "https://api.spotify.com/v1/search?q="
            urlrequest = urlrequest + searchgenre +"&type=playlist"
            data = json.loads(urllib.urlopen(urlrequest).read())
            totalPlaylists = len(data["playlists"]['items'])
            print "total Playlists"
            print totalPlaylists
            return data["playlists"]['items'][randint(0,totalPlaylists-1)]['uri']



        uriSpot = "https://embed.spotify.com/?uri="+spot(demo_db['music'])+"&theme=white"
     




        def pullQuote():
            """
            No input needed - for now.
            Output: [quote, author]
            """

            conn = sqlite3.connect('motiveQuote.db')
            c = conn.cursor()
            #sql = "SELECT * FROM stuffToPlot WHERE majortheme =?"

            # Select a random row in the DB of quotes.
            # [0]: quote number; [1] quote, [2] author, [3] major theme, [4] minor theme
            sql = c.execute("SELECT * FROM stuffToPlot ORDER BY RANDOM() LIMIT 1")

            results = sql.fetchall()
            quote = results[0][1]
            author = results[0][2]
            return [quote,author]

        def getLongYoutube(args):
            """
            input: youtube video ID
            output: full Youtube link
            """
            longYoutube = "https://www.youtube.com/watch?v="+args
            return longYoutube


        def saveAndShorten(args):
            """
            input: longlink
            output: shortlink
            """
            def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
                solution = ''.join(random.choice(chars) for _ in range(size))
                return solution

            # the function findKey is useful to render the index.html template with the short link stored as a key in our dictionary
            #def findKey(): 
            #    for sh_link, lo_link in db.items():
            #        if lo_link == longLinkText:
            #            return sh_link


            #before: generateRandomAndSave(longLinkText)


            def findKey(valeur):
                for key, value in db.items():
                    if value == valeur:
                        return key


            def generateRandomAndSave(args):
                shortRandomLink = str(id_generator())
                if db.has_key(shortRandomLink):
                    generateRandomAndSave(args)   #if short link already exists, regenerate a random URL -> recursive function
                else:
                    if args in db.values():
                        return findKey(args)
                    else:
                        db[shortRandomLink] = args
                        return findKey(args)

            generateRandomAndSave(args)
            shortYout = "http://localhost:5000/short/"+findKey(args)
            return shortYout


        longvideo = getLongYoutube(youtube_search(demo_db['pets'])[1])




        def demand(host, path, url_params=None):
            """Prepares OAuth authentication and sends the request to the API.
            Args:
                host (str): The domain host of the API.
                path (str): The path of the API after the domain.
                url_params (dict): An optional set of query parameters in the request.
            Returns:
                dict: The JSON response from the request.
            Raises:
                urllib2.HTTPError: An error occurs from the HTTP request.
            """
            url_params = url_params or {}
            url = 'https://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

            consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
            oauth_request = oauth2.Request(
                method="GET", url=url, parameters=url_params)

            oauth_request.update(
                {
                    'oauth_nonce': oauth2.generate_nonce(),
                    'oauth_timestamp': oauth2.generate_timestamp(),
                    'oauth_token': TOKEN,
                    'oauth_consumer_key': CONSUMER_KEY
                }
            )
            token = oauth2.Token(TOKEN, TOKEN_SECRET)
            oauth_request.sign_request(
                oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
            signed_url = oauth_request.to_url()

            conn = urllib2.urlopen(signed_url, None)
            try:
                response = json.loads(conn.read())
            finally:
                conn.close()

            return response


        def search(term, location):
            """Query the Search API by a search term and location.
            Args:
                term (str): The search term passed to the API.
                location (str): The search location passed to the API.
            Returns:
                dict: The JSON response from the request.
            """

            url_params = {
                'term': term.replace(' ', '+'),
                'location': location.replace(' ', '+'),
                'limit': SEARCH_LIMIT
            }
            return demand(API_HOST, SEARCH_PATH, url_params=url_params)


        def get_business(business_id):
            """Query the Business API by a business ID.
            Args:
                business_id (str): The ID of the business to query.
            Returns:
                dict: The JSON response from the request.
            """
            business_path = BUSINESS_PATH + business_id

            return demand(API_HOST, business_path)


        def query_api(term, location):
            """Queries the API by the input values from the user.
            Args:
                term (str): The search term to query.
                location (str): The location of the business to query.
            """
            response = search(term, location)

            businesses = response.get('businesses')

            busRandom = random.randint(0,len(businesses)-1)

            business_id = businesses[busRandom]['id']

            #[dict of longitude and latitude, business name]
            response = [get_business(business_id)['location']['coordinate'],get_business(business_id)['name'],get_business(business_id)['location']['display_address']]

            return response

        foodSearch = demo_db['food'][randint(0,len(demo_db['food'])-1)]
        print "foodSearch-----------"
        print foodSearch
        print "latitude ----------"
        latitude = query_api(foodSearch,"Berkeley")[0]['latitude']
        print latitude
        print "longitude ----------"
        longitude = query_api(foodSearch,"Berkeley")[0]['longitude']
        print longitude
        foodPlaceName = query_api(foodSearch,"Berkeley")[1]
        foodPlaceAdd = query_api(foodSearch,"Berkeley")[2]
        addTot = ''
        for item in foodPlaceAdd:
            addTot = addTot + item + ' '
    

        return flask.render_template('all.html', \
            youtubeId = youtube_search(demo_db['pets'])[1], \
            gifurl = searchGifOnGiphy(demo_db['gifs']), \
            quote = pullQuote()[0], quoteauthor = pullQuote()[1], \
            spotifyURL = uriSpot,\
            shortYoutLink = saveAndShorten(longvideo),\
            foodPlace = foodPlaceName,\
            latitude = latitude,\
            longitude = longitude, \
            addTot = addTot)




##################################################
##################################################
##################################################
##################################################


##################################################
##################################################
##################################################


@app.route("/short/<short>", methods=['GET'])
def redirige(short):
    """
    Redirect the request to the URL associated =short=, otherwise return 404
    NOT FOUND
    """
    short = str(short)

    if db.has_key(short) == True:
        return redirect(db[short], code=302)
    else:
        return flask.render_template('404.html')

    #raise NotImplementedError







if __name__ == "__main__":
    app.run()
