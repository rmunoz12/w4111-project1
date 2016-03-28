#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import click
import json
from math import floor
import os
import re
import traceback

from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, \
                  session, url_for

import qry


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#

# Example for local config.json:
# ---
# {
#     "db_path": "postgresql://Rich@localhost/Rich"
# }


with open('config.json') as f:
    config = json.load(f)
DATABASEURI = config['db_path']

app.secret_key = config['secret']

engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request

    The variable g is globally accessible
    """
    print "request: %s" % request
    print "request.form: %s" % request.form
    try:
        g.conn = engine.connect()
    except:
        print "uh oh, problem connecting to database"
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


def user_dashboard():
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']

    cursor = qry.friends(g.conn, uid)
    friends = {}
    for r in cursor:
        friends[r['friend_uid']] = r
    cursor.close()

    cursor = qry.not_friends(g.conn, uid)
    not_friends = {}
    for r in cursor:
        not_friends[r['uid']] = r
    cursor.close()

    cursor = qry.artist_follows(g.conn, uid)
    artist_follows = {}
    for r in cursor:
        artist_follows[r['aid']] = r
    cursor.close()

    cursor = qry.not_followed(g.conn, uid)
    not_followed = {}
    for r in cursor:
        not_followed[r['aid']] = r
    cursor.close()

    cursor = qry.playlist_subscribed(g.conn, uid)
    playlist_subscribed = {}
    for r in cursor:
        playlist_subscribed[r['pid']] = r
    cursor.close()

    cursor = qry.playlist_created(g.conn, uid)
    playlist_created = {}
    for r in cursor:
        playlist_created[r['pid']] = r
    cursor.close()

    cursor = qry.playlist_not_subscribed(g.conn, uid)
    playlist_not_subscribed = {}
    for r in cursor:
        k = str(r['creater_uid']) + "|" + str(r['pid'])
        playlist_not_subscribed[k] = r
    cursor.close()


    context = dict(user=name, friends=friends, not_friends=not_friends,
                   artist_follows=artist_follows, not_followed=not_followed,
                   playlist_subscribed=playlist_subscribed,
                   playlist_created=playlist_created,
                   playlist_not_subscribed=playlist_not_subscribed)
    return render_template('user-dashboard.html', **context)


@app.route('/')
def index():
    if 'uid' in session:
        return user_dashboard()
    cursor = g.conn.execute("SELECT uid, uname FROM users")
    users = {}
    for result in cursor:
        users[result['uid']] = result['uname']
    cursor.close()

    context = dict(data=users, bad_uname=session.get('bad_uname'))
    session['bad_uname'] = False
    return render_template("index.html", **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['uid'] = request.form['uid']
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('uid', None)
    return redirect(url_for('index'))


@app.route('/add-friend', methods=['POST'])
def add_friend():
    if 'uid' not in session:
        print("reached /add-friend with no session['uid']; return to index")
        return redirect(url_for('index'))
    cursor = qry.add_friend(g.conn, session['uid'], request.form['uid'])
    cursor.close()
    return redirect(url_for('index'))


@app.route('/remove-friend', methods=['POST'])
def remove_friend():
    if 'uid' not in session:
        print("reached /remove-friend with no session['uid']; return to index")
        return redirect(url_for('index'))
    cursor = qry.delete_friend(g.conn, session['uid'],
                               request.form['delete_uid'])
    cursor.close()
    return redirect(url_for('index'))


@app.route('/add-artist', methods=['POST'])
def add_artist():
    if 'uid' not in session:
        print("reached /add-artist with no session['uid']; return to index")
        return redirect(url_for('index'))
    cursor = qry.add_artist(g.conn, session['uid'], request.form['aid'])
    cursor.close()
    return redirect(url_for('index'))


@app.route('/remove-artist', methods=['POST'])
def remove_artist():
    if 'uid' not in session:
        print("reached /remove-artist with no session['uid']; return to index")
        return redirect(url_for('index'))
    cursor = qry.delete_artist(g.conn, session['uid'],
                               request.form['delete_aid'])
    cursor.close()
    return redirect(url_for('index'))

@app.route('/add-playlist', methods=['POST'])
def add_playlist():
    if 'uid' not in session:
        print("reached /add-playlist with no session['uid']; return to index")
        return redirect(url_for('index'))
    t, r = request.form['pid'].split("|")
    cursor = qry.add_playlist(g.conn, session['uid'], t, r)
    cursor.close()
    return redirect(url_for('index'))

@app.route('/remove-playlist', methods=['POST'])
def remove_playlist():
    if 'uid' not in session:
        print("reached /remove-playlist with no session['uid']; return to index")
        return redirect(url_for('index'))
    cursor = qry.remove_playlist(g.conn, session['uid'],
                                 request.form['remove_pid'],
                                 request.form['remove_cid'])
    cursor.close()
    return redirect(url_for('index'))

@app.route('/new-user', methods=['POST'])
def new_user():
    uname = request.form['uname']
    pattern = '^[a-z A-Z][a-zA-Z0-9]*$'
    if re.match(pattern, uname):
        cursor, uid = qry.new_user(g.conn, request.form['uname'])
        cursor.close()
        session['uid'] = uid
    else:
        session['bad_uname'] = True
    return redirect(url_for('login'))


@app.route('/delete-user')
def delete_user():
    if 'uid' not in session:
        print("reached /delete-user with no session['uid']; return to index")
        return redirect(url_for('index'))
    cursor = qry.delete_user(g.conn, session['uid'])
    cursor.close()
    return redirect(url_for('logout'))


@app.route('/delete-playlist', methods=['POST'])
def delete_playlist():
    if 'uid' not in session:
        print("reached /delete-playlist with no session['uid']; return to index")
        return redirect(url_for('index'))
    cursor = qry.delete_playlist(g.conn, request.form['delete_pid'],
                                 request.form['delete_cid'])
    cursor.close()
    return redirect(url_for('index'))


@app.route('/songs', methods=['POST'])
def songs():
    if 'uid' not in session:
        print("reached /songs with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']

    cursor = qry.liked_songs(g.conn, uid)
    likes = set()
    for r in cursor:
        likes.add(r['sid'])
    cursor.close()

    cursor = qry.search_songs(g.conn, request.form['song'])
    songs = {}
    for r in cursor:
        d = dict(r)
        if d['sid'] in likes:
            d['liked'] = True
        else:
            d['liked'] = False
        songs[d['sid']] = d
    cursor.close()

    context = dict(user=name, songs=songs)
    return render_template("songs.html", **context)

@app.route('/songspl', methods=['POST'])
def songspl():
    if 'uid' not in session:
        print("reached /songspl with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']
    cursor = qry.songsinpl(g.conn, request.form['pid'])
    songsinpl = set()
    for r in cursor:
        songsinpl.add(r['sid'])
    cursor.close()

    cursor = qry.search_songs(g.conn, request.form['song'])
    songs = {}
    for r in cursor:
        d = dict(r)
        if d['sid'] in songsinpl:
            d['liked'] = True
        else:
            d['liked'] = False
        songs[d['sid']] = d
    cursor.close()

    context = dict(user=name, songs=songs, pid=request.form['pid'])
    return render_template("songspl.html", **context)


@app.route('/createplaylist')
def createplaylist():
    if 'uid' not in session:
        print("reached /createplaylist with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']
    context = dict(user=name)
    return render_template("createplaylist.html", **context)

@app.route('/createpl', methods=['POST'])
def createpl():
    if 'uid' not in session:
        print("reached /createpl with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']
    cursor = qry.createpl(g.conn, uid, request.form['playlist'])
    cursor.close()
    pid = qry.pidpl(g.conn).first()['pid']
    
    songs1 = {}
    #plname = qry.playlist_name(g.conn, pid, uid).first()['pname']
    likes = set()
    context = dict(user=name, songs1=songs1, pname=request.form['playlist'], likes=likes, pid=pid,
                   cid=uid)
    return render_template("playlist.html", **context)


@app.route('/playlist')
def playlist():
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']
    if not request.args.get('pid'):
        return "No pid passed"
    pid = request.args['pid']
    cid = request.args['cid']
    cursor = qry.playlist_songs(g.conn, pid, cid)
    songs1 = {}
    for r in cursor:
        songs1[r['sid']] = r
    cursor.close()
    plname = qry.playlist_name(g.conn, pid, cid).first()['pname']

    cursor = qry.liked_songs(g.conn, uid)
    likes = set()
    for r in cursor:
        likes.add(r['sid'])
    cursor.close()

    context = dict(user=name, songs1=songs1, pname=plname, likes=likes, pid=pid,
                   cid=cid)
    return render_template('playlist.html', **context)

@app.route('/add_song_to_playlist')
def add_song_to_playlist():
    if 'uid' not in session:
        print("reached /add_song_to_playlist with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']
    pid = request.args['pid']

    cursor = qry.songsinpl(g.conn, pid)
    songsinpl = set()
    for r in cursor:
        songsinpl.add(r['sid'])
    cursor.close()

    cursor = qry.liked_songs(g.conn, uid)
    likes = {}

    for r in cursor:
        d = dict(r)
        if d['sid'] in songsinpl:
            d['liked'] = True
        else:
            d['liked'] = False
        likes[d['sid']] = d
    cursor.close()

    context = dict(user=name, likes=likes, pid=pid)
    return render_template('addsongs.html', **context)

@app.route('/addtopl', methods=['POST'])
def addtopl():
    if 'uid' not in session:
        print("reached /addtopl with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']

    cursor = qry.addtopl(g.conn, request.form['add_sid'], request.form['pid'])
    cursor.close()
    return redirect(url_for('index'))


@app.route('/artist')
def artist():
    if 'uid' not in session:
        print("reached /artist with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']

    if not request.args.get('aid'):
        return "No aid passed"
    aid = request.args['aid']
    cursor = qry.aname(g.conn, aid)
    r = cursor.first()
    if not r:
        return "Unrecognized aid"
    aname = r['aname']
    cursor.close()

    cursor = qry.publish(g.conn, aid)
    albums = []
    for r in cursor:
        d = {r['albumid']: r}
        albums.append(d)
    cursor.close()

    songs_by_album = {}
    for d in albums:
        for albumid, r in d.items():
            cursor = qry.list_album_songs(g.conn, albumid)
            songs = []
            for row in cursor:
                songs.append(row)
            cursor.close()
            songs_by_album[albumid] = songs

    cursor = qry.liked_songs(g.conn, uid)
    likes = set()
    for r in cursor:
        likes.add(r['sid'])
    cursor.close()

    context = dict(aid=aid, aname=aname, albums=albums,
                   songs_by_album=songs_by_album, user=name, likes=likes)
    return render_template('artist.html', **context)


@app.route('/song')
def song():
    if 'uid' not in session:
        print("reached /song with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']

    if not request.args.get('sid'):
        return "No sid passed"
    sid = request.args['sid']
    cursor = qry.song_details(g.conn, sid)
    r = cursor.first()
    if not r:
        return "Unrecognized sid"
    song_details = dict(r)
    cursor.close()

    song_details['minutes'] = int(floor(song_details['length'] / 1000 / 60))
    song_details['seconds'] = (song_details['length'] -
                               song_details['minutes'] * 1000 * 60) / 1000
    song_details['seconds'] = int(round(song_details['seconds']))

    cursor = qry.liked_songs(g.conn, uid)
    likes = set()
    for r in cursor:
        likes.add(r['sid'])
    cursor.close()

    liked = False
    if sid in likes:
        liked = True

    context = dict(user=name, song_details=song_details, liked=liked)
    return render_template('song-details.html', **context)


@app.route('/library')
def library():
    if 'uid' not in session:
        print("reached /library with no session['uid']; return to index")
        return redirect(url_for('index'))
    uid = session['uid']
    name = qry.uname(g.conn, uid).first()['uname']

    cursor = qry.liked_songs(g.conn, uid)
    likes = []
    for r in cursor:
        likes.append(r)
    cursor.close()

    context = dict(user=name, likes=likes)
    return render_template('library.html', **context)


@app.route('/unlike', methods=['POST'])
def unlike():
    if 'uid' not in session:
        print("reached /unlike with no session['uid']; return to index")
        return redirect(url_for('index'))
    cursor = qry.unlike(g.conn, session['uid'], request.form['unlike_sid'])
    cursor.close()
    return redirect(url_for('library'))


@app.route('/like-or-unlike', methods=['POST'])
def like_or_unlike():
    if 'uid' not in session:
        print("reached /unlike with no session['uid']; return to index")
        return redirect(url_for('index'))
    if request.form['submit'] == '+':
        cursor = qry.like(g.conn, session['uid'], request.form['sid'])
        cursor.close()
    else:
        cursor = qry.unlike(g.conn, session['uid'], request.form['sid'])
        cursor.close()
    if not request.form.get('redirect'):
        return redirect(url_for('index'))
    if request.form['redirect'] == 'artist':
        return redirect(url_for('artist', aid=request.form['aid']))
    if request.form['redirect'] == 'song':
        return redirect(url_for('song', sid=request.form['sid']))
    if request.form['redirect'] == 'playlist':
        return redirect(url_for('playlist', pid=request.form['pid'],
                                cid=request.form['cid']))
    return redirect(url_for('index'))


@app.route('/remove-playlist-song', methods=['POST'])
def remove_playlist_song():
    if 'uid' not in session:
        print("reached /remove-playlist-song with no session['uid']; return to index")
        return redirect(url_for('index'))
    pid = request.form['pid']
    cid = request.form['cid']
    sid = request.form['sid']

    cursor = qry.remove_playlist_song(g.conn, cid, pid, sid)
    cursor.close()

    return redirect(url_for('playlist', pid=pid, cid=cid))


if __name__ == "__main__":
    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using

            python server.py

        Show the help text using

            python server.py --help

        """
        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
