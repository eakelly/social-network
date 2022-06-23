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

import application.login
import application.user_info
import application.admin_page
import application.user_profile
import application.edit_profile


with open(conf_dir + '/config.json') as f:
  config = json.load(f)


DATABASEURI = "postgresql://" + config['user'] + ":" + config['password'] + "@35.196.192.139:5432/proj1part2"

engine = create_engine(DATABASEURI)

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
      # If admin user, redirect to admin page
      if userid == '0':
          return redirect("/admin_page/0")
      else:
        return redirect("/user_info/{}".format(user.first()[0]))

    except Exception as e:
      print(e)
      return render_template('index.html', error='Login Failed. User ID or Password is incorrect. Please try again.')


@app.route('/user_info/<string:id>', methods=["GET", "POST"])
def user_info(id):

  # Check error in query string when posting a message fails
  error = ''
  error_msg = request.args.get('error')
  if error_msg: error = error_msg

  if "POST" == request.method:
    try:
        content = request.form['create_post']
        profile_id = request.form['profile_id']
        user = g.conn.execute("INSERT INTO posts(user_id, profile_id, content) VALUES ({}, {}, '{}') RETURNING user_id".format(id, profile_id, content))
    except Exception as e:
         print(e)
         error = "Creating a new post failed. Try again"
         return redirect("/user_info/{}?error={}".format(id,error));
    return redirect("/user_info/{}".format(id));

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

  return render_template('user_info.html', info=user_info, friends=user_friends, posts=user_posts, locations=user_locations, profiles=user_profiles, error = error)


@app.route('/edit_profile/<string:userid>/<string:profileid>', methods=["GET", "POST"])
def edit_profile(userid, profileid):
  if "POST" == request.method:
    try:
        bio = request.form['bio']
        g.conn.execute("UPDATE profiles SET bio = '{}' WHERE user_id = {} AND profile_id = {}".format(bio, userid, profileid))
    except Exception as e:
        print(e)
        error = "Error updating profile. Try again!"
        return render_template('edit_profile.html', user_id=userid, profile_id=profileid, error=error)
    return redirect("/user_info/user_profile/{}/{}".format(userid, profileid))

  return render_template('edit_profile.html', user_id=userid, profile_id=profileid)


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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
      try:
        first_name = request.form['first_name']
        middle_name = request.form['middle_name']
        last_name = request.form['last_name']
        age = request.form['age']
        password = request.form['password']

        user = g.conn.execute("INSERT INTO users(first_name, middle_name, last_name, age, password) VALUES ('{}', '{}', '{}', {}, '{}') RETURNING user_id".format(first_name, middle_name, last_name, age, password))
        return redirect("/user_info/{}".format(user.first()[0]))

      except Exception as e:
           print(e)
           error = "Error in sign up. Ensure to fill in all the required values and note that you must be 13years or above !"
           return render_template('index.html', error = error);
    else:
        return render_template('index.html')


@app.route('/admin_page/<string:id>', methods=["GET", "POST"])
def admin_page(id):

  filter = {"state":"none", "users":[]}
  try:
      if "POST" == request.method:
          input_state  = request.form['state_name']
          query =  text("SELECT U.first_name, U.last_name  \
                          FROM Users U,(SELECT I.user_id \
                                        FROM located_in I, locations L \
                                        WHERE I.zipcode = L.zipcode \
                                              AND L.state_name = '{}')\
                                        AS state_users \
                          WHERE state_users.user_id = U.user_id; \
                          ".format(input_state))
          cursor = g.conn.execute(query)
          for c in cursor:
              filter["users"].append(c)
          filter["state"] = input_state
  except Exception as e:
        print(e)

  user_info_query = application.user_info.fetch_user_info(id)
  user_info = g.conn.execute(user_info_query)

  admin_page_locations_query = application.admin_page.fetch_locations()
  admin_page_locations = g.conn.execute(admin_page_locations_query)

  avg_age_of_friends_query = application.admin_page.get_avg_age_of_friends()
  avg_age_of_friends = g.conn.execute(avg_age_of_friends_query)

  post_stats_query = application.admin_page.get_post_stats()
  post_stats = g.conn.execute(post_stats_query)

  all_states = g.conn.execute("SELECT DISTINCT state_name from locations;")

  return render_template('admin_page.html', info=user_info, locations=admin_page_locations, avg_age_of_friends=avg_age_of_friends, post_stats=post_stats, all_states=all_states, filter=filter)

@app.route("/delete_post", methods=['GET'])
def delete():
    post_id = request.args.get('post_id', None)
    user_id = request.args.get('user_id', None)
    if post_id == None:
        return redirect("/user_info")

    try:
        query = text("DELETE from posts where post_id={} and user_id={};".format(post_id, user_id))
        g.conn.execute(query)
    except Exception as e:
        print(e)

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
