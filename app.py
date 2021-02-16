import json
import sys
import time
import os
import subprocess
from flask import Flask, request, render_template,\
    redirect, send_file, send_from_directory,\
    url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from utils import calculateRank

app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///User.sqlite3'

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"
    guid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    score = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    country = db.Column(db.String(5))
    #keeping the database sorted by score would help 
    #as it lowers displaying rank to log(n) and 
    #insertion to O(n) as you shift the rest by one
    #I could do some freaky stuff with lambda and redis

class Scores(db.Model):
    __tablename__ = "scores"
    score = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    roflm = db.Column(db.Integer)
    #this essentially is a vector, I do not have details regarding the score system 
    #therefore I'll assume it is 0 to ~13k integer
    #it speeds up the rank calculation.

@app.route('/leaderboard')
def leaderboard_global():
    #there seems to be no pagination?
    #are you sure you want it to return 5m results at once in a single response?
    return ''

@app.route('/leaderboard/<country_iso_code>')
def leaderboard_country(country_iso_code):
    #I'm assuming you expect me to get the country from user's IP adress.
    #keeping this one under 1 second will be hard for countries with bad scores.
    #luckily you'll need vpn to submit with a different country.
    return ''

@app.route('/score/submit')
def submit_score():
    if request.method == 'POST':
        score=request.json['score']

@app.route('/user/profile/<user_guid>')
def user_profile(user_guid):
    return ''

@app.route('/user/create')
def user_create():
    if request.method == 'POST':
        country=""
        try:
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            #country = curl 'ipinfo.io/'+ip -silent | grep -iE '^ *"country":' | awk '{print $2}' 
            country = country[1:3].lower()
        except:
            country = " "
        try:
            user_id = request.json["user_id"]
            display_name = request.json["display_name"]
            points = request.json["points"]
            rank = request.json["rank"]
            #this is stupid, I decide rank not you. I'll ignore it.
        except:
            return 404
        #fun begins here, db stuff.
            
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
