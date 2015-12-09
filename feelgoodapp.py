#!/usr/bin/env python

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

import requests
import base64
import pprint


# Libraries for QUOTE database:
from xlrd import open_workbook
import sqlite3
from sqlite3 import OperationalError
import time
import datetime


# Libraries for flask
import flask
from flask import request, Flask, render_template, jsonify, abort, redirect, make_response, g




print "######## FEEL-GOOD OF FACEBOOKAPP.PY ###########"
print "########################################"

# Project id value is retrieved from Google Developer Console
# on which I created a project called info253-feel-good
# and for which I have enabled YouTube API
project_id = 'info253-feel-good'


#create application
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


################################################################


demo_db = shelve.open("demo_db")



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

@app.route("/tastes", methods=['GET'])
def tastes():
    return flask.render_template('usertastes.html')





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
        print "demo_db"


        """
        CURRENTFEELING for GIPHY API
        """
        feeling = request.form.getlist('gifs')
        feelings = []
        for item in feeling:
            item = str(item).replace('u\'','')
            feelings.append(item)
        feeling = feelings
        print "gifs ", feeling
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



        print demo_db['pets']




    

        return flask.render_template('all.html', \
            youtubeId = youtube_search(demo_db['pets'])[1], \
            gifurl = searchGifOnGiphy(demo_db['gifs']), \
            quote = pullQuote()[0], quoteauthor = pullQuote()[1], \
            spotifyURL = "Spotify not ready yet")





#@app.route("/")
@app.route("/spotifylogin")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    #get Category of music
    musicGenre = "rnb"
    print "------------"
    print "musicGenre ", musicGenre
    categories_api_endpoint = "{}/browse/categories/{}/playlists".format(SPOTIFY_API_URL,musicGenre)
    print categories_api_endpoint
    categories_response = requests.get(categories_api_endpoint, headers=authorization_header)
    categories_data = json.loads(categories_response.text)
    

    pp = pprint.PrettyPrinter(indent=2)
    #change index 0 to select random list in pop
    #pp.pprint(categories_data['playlists']['items'][2]['uri'])

    print "the URI is"
    playlistURI = categories_data['playlists']['items'][2]['uri']
    print "--->", playlistURI

    response = make_response(render_template('all.html'))
    response.headers['Authorization'] = authorization_header['Authorization']



    uriSpotify = "https://embed.spotify.com/?uri=" + playlistURI + "&theme=white"
    return render_template("index2.html",uriSpotify = uriSpotify)





if __name__ == "__main__":
    app.run()
