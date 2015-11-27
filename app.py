#!/usr/bin/env python
import shelve
from subprocess import check_output
import flask
from flask import request, Flask, render_template, jsonify, abort, redirect
from os import environ

import os
import sys
import json
import hashlib

import string
import random




app = flask.Flask(__name__)
app.debug = True

# Database/Dictionary to save shortened URLs
db = shelve.open("shorten.db")

@app.route('/')
def index():
    """
    Builds a template based on a GET request, with some default
    arguments
    """
    return flask.render_template('index.html')

###
# Now we'd like to do this generally:
# <short> will match any word and put it into the variable =short= Your task is
# to store the POST information in =db=, and then later redirect a GET request
# for that same word to the URL provided.  If there is no association between a
# =short= word and a URL, then return a 404
###


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    solution = ''.join(random.choice(chars) for _ in range(size))
    return solution


@app.route("/create", methods=['POST'])
def create():
    """
    This POST request creates an association between a short url and a full url
    and saves it in the database (the dictionary db)
    """

# the function findKey is useful to render the index.html template with the short link stored as a key in our dictionary
    def findKey(longLinkText): 
        for sh_link, lo_link in db.items():
            if lo_link == longLinkText:
                return sh_link

    def generateRandomAndSave(longLinkText):
        shortRandomLink = str(id_generator())
        if db.has_key(shortRandomLink):
            generateRandomAndSave(longLinkText)   #if short link already exists, regenerate a random URL -> recursive function
        else:
            db[shortRandomLink] = longLinkText


# we retrieve the inputs from the form. There is the choice of the user, the long link, and the name the user wants to give to the new URL

    button = request.form['userChoice']  # there are 2 cases: either user wants to choose the name of the short URL him/herself OR
                                        # it asks for it to be generated randomly.
    longLinkText = str(request.form['longLink'])

    shortUserLinkText = str(request.form['shortUserLink'])



# this is the case where the user wants to name him/herself the new url
    if button == '1':

        if longLinkText in db.values(): # if the long link is already stored in our dictionary, we return the old value we stored.
                                        # we do so, even if the user wants to give it a new name.
            db[findKey(longLinkText)] = longLinkText


        else:
            if db.has_key(shortUserLinkText):
                generateRandomAndSave(longLinkText)   #if short link already exists, regenerate a random URL (see function)
            else:
                db[shortUserLinkText] = longLinkText


    elif button == '2':   # User wants to randomize the name of the new URL (this is for extra credit)

        if longLinkText in db.values():  #If the long URL already exists in the DB, we give it its old short URL
                                        # Note that the short URL could be either a name that the user gave in the past, or a random
                                        # number that the user asked for in the past.
            db[findKey(longLinkText)] = longLinkText
        else:
            generateRandomAndSave(longLinkText)

    return render_template("index.html", shortlink=findKey(longLinkText))

    #raise NotImplementedError



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
