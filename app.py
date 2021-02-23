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


def calculate_rank(score):
    # TODO count the rank using scores table
    # could improve user creation time by
    # returning number of rows in user table +1
    return 0


def run_command(cmd):
    print("Running command: {}".format(cmd))
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=False
    )
    # simple running of command
    stdout, stderr = p.communicate()
    stdout = stdout.decode("utf8", errors='replace')
    stderr = stderr.decode("utf8", errors='replace')
    print(stdout)
    if p.returncode == 0:
        return stdout
    else:
        raise RuntimeError(
            "Error running command {}: {}".format(cmd, str(stderr)))


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
    # keeping the database sorted by score would help
    # as it lowers displaying rank to log(n) and
    # insertion to O(n) as you shift the rest by one
    # I could do some freaky stuff with lambda and redis


class Scores(db.Model):
    __tablename__ = "scores"
    score = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    # roflm = db.Column(db.Integer) calculating this on the go makes no diff.

    # this essentially is a vector,
    # I do not have details regarding the score system
    # therefore I'll assume it is 0 to ~13k integer
    # it speeds up the rank calculation.


@app.route('/leaderboard')
def leaderboard_global():
    # there seems to be no pagination?
    # are you sure you want it to return
    # 5m results at once in a single response?
    return ''


@app.route('/leaderboard/<country_iso_code>')
def leaderboard_country(country_iso_code):
    # I'm assuming you expect me to get the country from user's IP adress.
    # keeping this one under 1 second will be hard
    # for countries with bad scores.
    # luckily you'll need vpn to submit with a different country.
    return ''


@app.route('/score/submit')
def submit_score():
    if request.method == 'POST':
        score = request.json['score']


@app.route('/user/profile/<user_guid>')
def user_profile(user_guid):
    try:
        query = User.query.filter_by(guid=user_guid)
        user = query.one()
        data = {'user_id': user.guid,
                "display_name": user.name,
                "points": user.score,
                "rank": user.rank}
        return data, 200
    except:
        data = {'message': 'user not found'}
        return data, 404


@app.route('/user/create', methods=['POST'])
def user_create():
    if request.method == 'POST':
        country = ""
        # to avoid the warning caused by conditional variable definition
        try:
            country = request.json["country"]
        except:
            try:
                # try to get the current location of the user
                ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
                ipinfo = str(run_command([
                    'curl', f'ipinfo.io/{ip}', '-silent']))
                ct_index = ipinfo.find('"country": "')+len('"country": "')
                country = ipinfo[ct_index:ct_index+2].lower()
            except:
                country = " "
        try:
            user_id = request.json["user_id"]
            # I guess I'm supposed to generate the guid
            # rather than frontend, will be this way for now
            display_name = request.json["display_name"]
            points = 0
        except:
            data = {'message': 'missing parameters'}
            return data, 404
        try:
            query = User.query.filter_by(guid=user_id)
            # TODO remove this query and generate guid
            user = query.one()
            data = {'message': 'an account with this guid already exists'}
            return data, 418
            # teapot but there was an actual code for this
            # TODO replace with proper error code
        except:  # sqlalchemy.orm.exc.NoResultFound
            # should be here, this is a bad idea
            rank = calculate_rank(int(points))
            user = User(
                guid=str(user_id),
                name=str(display_name),
                score=int(points),
                rank=int(rank),
                country=str(country))
            try:
                db.session.add(user)
                db.session.commit()
                data = {'user_id': user_id,
                        "display_name": display_name,
                        "points": int(points),
                        "rank": int(rank)}
                return data, 200
                # This would be 302 but somehow it does not support
                # request payload, did not happen before.
            except:
                data = {'message': 'something went wrong'}
                return data, 418
                # TODO replace with proper error code


if __name__ == "__main__":
    app.run(host='0.0.0.0')
