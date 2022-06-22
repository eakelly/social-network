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
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
conf_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config')
app = Flask(__name__, template_folder=tmpl_dir)
app.config["TEMPLATES_AUTO_RELOAD"] = True

import application.login
import application.user_info
import application.admin_page
import application.user_profile


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.152.219/proj1part2
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.152.219/proj1part2"
#

# Import login details from configuration file.
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


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
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
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')


@app.route('/login', methods=["GET"])
def login_render():
  if "GET" == request.method:
    query = application.login.fetch_users()
    cursor = g.conn.execute(query)
    result = []
    for c in cursor:
      result.append(c)
    return render_template("login.html", **dict(data = result))
  # else:
  #   query = application.login.
  #   cursor = g.conn.execute(query)
  #   med_ref = 0
  #   for c in cursor:
  #     med_ref = c
  #   query = application.medicines.add_medicine(med_ref[0],request.form)
  #   return redirect("/medicines")

@app.route('/user_info/<string:id>', methods=["GET"])
def user_info(id):
  if "GET" == request.method:
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

    # result = []
    # for c in cursor:
    #   result.append(c)
    # return render_template("user_info.html", **dict(data = result))
    return render_template('user_info.html', info=user_info, friends=user_friends, posts=user_posts, locations=user_locations, profiles=user_profiles)
  # else:
  #   query = application.login.
  #   cursor = g.conn.execute(query)
  #   med_ref = 0
  #   for c in cursor:
  #     med_ref = c
  #   query = application.medicines.add_medicine(med_ref[0],request.form)
  #   return redirect("/medicines")

@app.route('/user_info/user_profile/<string:userid>/<string:profileid>', methods=["GET"])
def user_profile(userid, profileid):
  if "GET" == request.method:
    user_info_query = application.user_profile.fetch_user_info(userid)
    user_info = g.conn.execute(user_info_query)

    user_profile_query = application.user_profile.fetch_profile(userid, profileid)
    user_profile = g.conn.execute(user_profile_query)

    profile_posts_query = application.user_profile.fetch_profile_posts(userid, profileid)
    profile_posts = g.conn.execute(profile_posts_query)

    # result = []
    # for c in cursor:
    #   result.append(c)
    # return render_template("user_info.html", **dict(data = result))
    return render_template('user_profile.html', info=user_info, profile=user_profile, posts=profile_posts)
  # else:
  #   query = application.login.
  #   cursor = g.conn.execute(query)
  #   med_ref = 0
  #   for c in cursor:
  #     med_ref = c
  #   query = application.medicines.add_medicine(med_ref[0],request.form)
  #   return redirect("/medicines")



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
