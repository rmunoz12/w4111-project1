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

import json
import os
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

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)

#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute(
    """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


#
# END SQLITE SETUP CODE
#



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


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/example')
def index_example():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print request.args

    #
    # example of a database query
    #
    cursor = g.conn.execute("SELECT aname FROM artists")
    names = []
    for result in cursor:
        names.append(result['aname'])  # can also be accessed using result[0]
    cursor.close()

    #
    # Flask uses Jinja templates, which is an extension to HTML where you can
    # pass data to a template and dynamically generate HTML based on the data
    # (you can think of it as simple PHP)
    # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
    #
    # You can see an example template in templates/index.html
    #
    # context are the variables that are passed to the template.
    # for example, "data" key in the context variable defined below will be
    # accessible as a variable in index.html:
    #
    #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
    #     <div>{{data}}</div>
    #
    #     # creates a <div> tag for each element in data
    #     # will print:
    #     #
    #     #   <div>grace hopper</div>
    #     #   <div>alan turing</div>
    #     #   <div>ada lovelace</div>
    #     #
    #     {% for n in data %}
    #     <div>{{n}}</div>
    #     {% endfor %}
    #
    context = dict(data=names)

    #
    # render_template looks in the templates/ folder for files.
    # for example, the below file reads template/index.html
    #
    return render_template("index-example.html", **context)


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

    context = dict(user=name, friends=friends, not_friends=not_friends,
                   artist_follows=artist_follows, not_followed=not_followed)
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

    context = dict(data=users)
    return render_template("index.html", **context)


@app.route('/login', methods=['POST'])
def login():
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


#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
    return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
    return redirect('/')


if __name__ == "__main__":
    import click


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
