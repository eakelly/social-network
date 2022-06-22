#!/usr/bin/env python

"""
Columbia's COMS W4111.003 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import json
# from app import app, db, login_manager
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from flask_login import current_user, login_user, logout_user, login_required, LoginManager

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
app = Flask(__name__, template_folder=tmpl_dir)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = "/login"
# login_manager.session_protection = "strong"

import application.login
import application.user_info
import application.admin_page
import application.user_profile
import application.edit_profile


with open(conf_dir + '/config.json') as f:
  config = json.load(f)


DATABASEURI = "postgresql://" + config['user'] + ":" + config['password'] + "@35.196.192.139:5432/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')


@app.route('/login', methods=["GET", 'POST'])
def login_render():
  if "GET" == request.method:
    query = application.login.fetch_users()
    cursor = g.conn.execute(query)
    result = []
    for c in cursor:
      result.append(c)
    return render_template("login.html", **dict(data = result))
  else:
    try:
      userid = request.form['user_id']
      password = request.form['password']
      user = g.conn.execute("SELECT * FROM users WHERE user_id = {} AND password = '{}'".format(userid, password))
      return redirect("/user_info/{}".format(user.first()[0]))
    except Exception as e:
      print(e)
      return render_template('index.html', error='User ID or Password is incorrect. Please try again.')


@app.route('/user_info/<string:id>', methods=["GET", "POST"])
def user_info(id):

  if "POST" == request.method:
    content = request.form['create_post']
    profile_id = request.form['profile_id']
    user = g.conn.execute("INSERT INTO posts(user_id, profile_id, content) VALUES ({}, {}, '{}') RETURNING user_id".format(id, profile_id, content))

  user_info_query = application.user_info.fetch_user_info(id)
  user_info = g.conn.execute(user_info_query)

  user_friends_query = application.user_info.fetch_user_friends(id)
  user_friends = g.conn.execute(user_friends_query)

  user_posts_query = application.user_info.fetch_user_posts(id)
  user_posts = g.conn.execute(user_posts_query)

  user_locations_query = application.user_info.fetch_user_locations(id)
  user_locations = g.conn.execute(user_locations_query)

  user_profiles_query = application.user_info.fetch_user_profiles(id)
  user_profiles = g.conn.execute(user_profiles_query)
  
  return render_template('user_info.html', info=user_info, friends=user_friends, posts=user_posts, locations=user_locations, profiles=user_profiles)


@app.route('/user_info/user_profile/<string:userid>/<string:profileid>/edit_profile', methods=["POST"])
def edit_profile(userid, profileid):
  if "POST" == request.method:
    bio = request.form['bio']
    # edit_profile_query = application.edit_profile.edit_profile_info(userid, profileid, bio)
    # edit_profile = g.conn.execute(edit_profile_query)
    g.conn.execute("UPDATE proile SET bio = {} WHERE user_id = {} AND profile_id = {}".format(bio, userid, profileid))
    # user = g.conn.execute("INSERT INTO users(first_name, middle_name, last_name, age, password) VALUES ('{}', '{}', '{}', {}, '{}') RETURNING user_id".format(first_name, middle_name, last_name, age, password))
    # return redirect("/user_info/{}/user_profile/{}/{}".format(userid, profileid))
    return render_template('edit_profile.html', update_info=bio, user_id=userid, profile_id=profileid)


@app.route('/user_info/user_profile/<string:userid>/<string:profileid>', methods=["GET"])
def user_profile(userid, profileid):
  if "GET" == request.method:
    user_info_query = application.user_profile.fetch_user_info(userid)
    user_info = g.conn.execute(user_info_query)

    user_profile_query = application.user_profile.fetch_profile(userid, profileid)
    user_profile = g.conn.execute(user_profile_query)

    profile_posts_query = application.user_profile.fetch_profile_posts(userid, profileid)
    profile_posts = g.conn.execute(profile_posts_query)

    return render_template('user_profile.html', info=user_info, profile=user_profile, posts=profile_posts)


# @app.route('/register', methods=['POST'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
#   return redirect('/')


# @app.route("/login", methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         try:
#             username = request.form['user id']
#             password = request.form['password']
#             print(username, password)
#             if not current_user.is_authenticated:
#                 user = FridgeUser.get(loginid=username)
#                 print(user)
#                 if user and password == user.password:
#                     login_user(user, remember=True)
#                 else:
#                     return render_template('login.html', error='Username or password incorrect!')
        
#         except Exception as e:
#             print(e)
#             return render_template('login.html', error='Server encountered an error. Please try again later.')

#     if current_user.is_authenticated:
#         return redirect("/dashboard")
#     else:
#         return render_template('login.html')

# @app.route("/register", methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # try:
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        age = request.form['age']
        password = request.form['password']

        user = g.conn.execute("INSERT INTO users(first_name, middle_name, last_name, age, password) VALUES ('{}', '{}', '{}', {}, '{}') RETURNING user_id".format(first_name, middle_name, last_name, age, password))
        # db.session.execute("INSERT INTO login(uid, loginid, password) VALUES ({}, '{}', '{}')".format(user.first()[0], loginid, password))
        # g.conn.commit()
        print('user', user)
        return redirect("/user_info/{}".format(user.first()[0]))

        # except Exception as e:
        #     print(e)
        #     # g.conn.rollback()
        #     return render_template('index.html', error='Server encountered an error. Please try again later.')
    else:
        return render_template('index.html')


@app.route('/admin_page/<string:id>', methods=["GET"])
def admin_page(id):
  if "GET" == request.method:
    user_info_query = application.user_info.fetch_user_info(id)
    user_info = g.conn.execute(user_info_query)

    admin_page_locations_query = application.admin_page.fetch_locations()
    admin_page_locations = g.conn.execute(admin_page_locations_query)
    return render_template('admin_page.html', info=user_info, locations=admin_page_locations)


@app.route("/delete_post", methods=['GET'])
# Todo: @login_required
def delete():
    post_id = request.args.get('post_id', None)
    user_id = request.args.get('user_id', None)
    if post_id == None:
        return redirect("/user_info")

# Todo: make sure the post belongs to the current user once current_user.id and login_required are implemented
#    fridgeUser = db.session.execute("SELECT * from fridge where uid={} and fid={}".format(current_user.id, fid)).all()
#    if len(fridgeUser) == 0:
#        return redirect("/dashboard")

    try:
        query = text("DELETE from posts where post_id={} and user_id={};".format(post_id, user_id))
        g.conn.execute(query)
        #Todo: implement logging query = "INSERT INTO log(fid, message) VALUES ({}, '{}')".format(fid, "User deleted a item in fridge {}: {}".format(fid, conid))
        #db.session.execute(query)
        #db.session.commit()
    except Exception as e:
        print(e)
    #    db.session.rollback()

    return redirect("/user_info/{}".format(user_id))



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
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
