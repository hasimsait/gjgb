import json
import sys
import time
import os
import subprocess
import psycopg2
from flask import Flask, request, render_template,\
    redirect, send_file, send_from_directory,\
    url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

def calculateRank (score):
    return 0

app = Flask(__name__)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
DATABASE_URL = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
conn = psycopg2.connect(DATABASE_URL, sslmode='require')

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    guid = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    score = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    country = db.Column(db.String(3))
    #keeping the database sorted by score would help 
    #as it lowers displaying rank to log(n) and 
    #insertion to O(n) as you shift the rest by one
    #I could do some freaky stuff with lambda and redis

class Scores(db.Model):
    __tablename__ = "scores"
    score = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    #roflm = db.Column(db.Integer) calculating this on the go makes no diff.
    
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

@app.route('/user/create', methods=['POST'])
def user_create():
    if request.method == 'POST':
        country = ""
        #to avoid the warning caused by conditional variable definition
        try:
            #get country from ip of the client, not reliable but I'm assuming it is not provided.
            ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            country = subprocess.run(['curl', f'ipinfo.io/{str(ip)}', '-silent', '|', 'grep', '-iE', "'^ *\"country\":'", '|', 'awk', "'{print $2}'"],stoud=subprocess.PIPE)
            country = country.stdout.decode('utf-8')[1:3].lower()
        except:
            country = " "
        try:
            user_id = request.json["user_id"]
            #I guess I'm supposed to generate the guid rather than frontend, will be this way for now
            display_name = request.json["display_name"]
            points = 0
        except:
            data={'message':'missing parameters'}
            return data, 404
        query = User.query.filter_by(guid=user_id)
        try:
            user = query.one()
            data={'message':'an account with this guid already exists'}
            return data,418 
            #teapot but there was an actual code for this
            #TODO replace with proper error code
        except: #sqlalchemy.orm.exc.NoResultFound #should be here, this is a bad idea
            rank=calculateRank(int(points))
            user = User(guid=str(user_id),name=str(display_name),score=int(points),rank=int(rank),country=str(country))
            try:
                db.session.add(user)
                db.session.commit()
                data={'user_id': user_id,"display_name":display_name,"points":int(points),"rank":int(rank)}
                return data,200 
                #This would be 302 but somehow it does not support request payload, did not happen before.
            except:
                data={'message':'something went wrong'}
                return data,418 
                #TODO replace with proper error code

if __name__ == "__main__":
    app.run(host='0.0.0.0')
