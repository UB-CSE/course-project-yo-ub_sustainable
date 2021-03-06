import os
import re

from hashlib import md5

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import flash
from flask_login import LoginManager
from flask_login import login_required
from flask import make_response
import MySQLdb
import pymysql.cursors

import random
from users import Users
#new import for custom challenge html page
from challenge import newChallenge

# mysql = MySQL()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        MYSQL_DATABASE_HOST='us-cdbr-east-02.cleardb.com',
        MYSQL_PORT=15551,
        MYSQL_DATABSE_USER='b33b6415873ff5',
        MYSQL_DATABASE_PASSWORD='d1a1b9a1',
        MYSQL_DATABASE_DB='heroku_1e2700f5b989c0b'
    )

    # login = LoginManager(app)
    # mysql.init_app(app)
   

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/dash")
    def dash():
        if session.get('logged_in') == True:
            connection = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                             user='b33b6415873ff5',
                             password='d1a1b9a1',
                             db='heroku_1e2700f5b989c0b',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                cursor.execute('SELECT saved, progress, completed FROM dashboard WHERE user = %s', (session['username']))
            challs = cursor.fetchone()
            if challs:
                sav = challs['saved'].split("|")
                pro = challs['progress'].split("|")
                com = challs['completed'].split("|")
                session['saved'] = sav
                session['progress'] = pro
                session['completed'] = com
            return render_template("userdashboard.html")
        else:
            msg = 'Please login to access user-only content'
            return render_template("login.html", error = msg)

    @app.route("/challenge")
    def chall():
        return render_template("challenge_list.html")
    
    @app.route("/challenge1")
    def chall_pg1():
        return render_template("challenge_pages/challenge1.html")
    
    @app.route("/challenge2")
    def chall_pg2():
        return render_template("challenge_pages/challenge2.html")

    @app.route("/challenge3")
    def chall_pg3():
        return render_template("challenge_pages/challenge3.html")

    @app.route("/challenge4")
    def chall_pg4():
        return render_template("challenge_pages/challenge4.html")

    @app.route("/challenge5")
    def chall_pg5():
        return render_template("challenge_pages/challenge5.html")
    
    @app.route("/challenge6")
    def chall_pg6():
        return render_template("challenge_pages/challenge6.html")

    #Addition for Custom Challenge
    @app.route("/challengeCustom")
    def chall_pg7():
        return render_template("challenge_pages/custom_challenge.html")

    #Addition for new Custom Challenge specific page
    @app.route("/newChallengeCustom")
    def chall_pg8():
        return render_template("new_custom_challenge.html", newCC = newChallenge)

    @app.route("/friends")
    def friend():
        if session.get('logged_in') == True:
            return render_template("friends.html",
                friendList=Users['friends'],
                notFriendList=Users['notFriends'])
        else:
            msg = 'Please login to access user-only content'
            return render_template("login.html", error = msg)

    @app.route("/publicProfileFriend")
    def publicProfileFriend():
        return render_template("publicProfileFriend.html")

    @app.route("/publicProfileNotFriend")
    def publicProfileNotFriend():
        return render_template("publicProfileNotFriend.html")


    @app.route("/login", methods = ['GET', 'POST'])
    def login():
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            # cur = mysql.connection.cursor()
            connection = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                             user='b33b6415873ff5',
                             password='d1a1b9a1',
                             db='heroku_1e2700f5b989c0b',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password, ))
            
            data = cursor.fetchone()
            # print(data)
            if data:
                session['logged_in'] = True
                session['id'] = data['id']
                session['username'] = data['username']
                session['fname'] = data['fname']
                session['lname'] = data['lname']
                if "picture" in data.keys():
                    session['pro_pic'] = data['picture']
                flash('You are logged in')
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('username', data['username'])
                resp.set_cookie('fname', data['fname'])
                resp.set_cookie('lname', data['lname'])
                
                flash('You are logged in')
                
                return resp

            else:
                msg = 'Invalid Credentials. Please try again.'
            connection.close()
        return render_template("login.html", error = msg)
    
     
    @app.route('/logout')
    def logout():
        session.pop('logged_in', None)
        session.pop('id', None)
        session.pop('username', None)
        
        resp = make_response(redirect(url_for('home')))
        
        resp.set_cookie('username', "", max_age = 0)
        resp.set_cookie('fname', "", max_age = 0)
        resp.set_cookie('lname', "", max_age = 0)
        
        flash('You are logged out.')
        return resp

    @app.route("/signup", methods = ['GET', 'POST'])
    def signup():
        msg = ''
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            fname = request.form['fname']
            lname = request.form['lname']
            connection2 = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                    user='b33b6415873ff5',
                    password='d1a1b9a1',
                    db='heroku_1e2700f5b989c0b',
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor)
            with connection2.cursor() as cursor2:
                cursor2.execute('SELECT * FROM accounts WHERE username = %s', (username,))
            data = cursor2.fetchone()
            if data:
                # Account already exists
                msg = 'Account already exists.'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                # Invalid email address
                msg = 'Inavlid email address.'
            elif not re.match(r'[A-Za-z0-9]+', username):
                # Invalid username
                msg = 'Username must only contain characters and numbers.'
            elif not username or not password or not email:
                # Form was not filled out
                msg = 'Please enter your information.'
            else:
                hash_str = md5(email.encode('utf-8')).hexdigest()
                complete_hash = ('https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(hash_str, 128))
                session['pro_pic'] = complete_hash
                with connection2.cursor() as cursor3:
                    cursor3.execute("INSERT INTO accounts VALUES (NULL, %s, %s, %s, %s, %s, %s)", (fname, lname, username, password, email, complete_hash))
                    cursor3.execute("INSERT INTO dashboard VALUES (%s, %s, %s, %s)", (username, "the Earth", "being sustainable", "sign up")) 

                connection2.commit()
                msg = 'You have successfully registered!'
                session['username'] = username
                session['fname'] = fname
                session['lname'] = lname
                session['email'] = email
                # msg = complete_hash
                # print(complete_hash)
            connection2.close()
        elif request.method == 'POST':
            #Form is empty
            msg = 'Please enter your information.'
        
        return render_template("signup.html", msg = msg)

    #function for custom challenge form
    @app.route("/addingcustom", methods = ['GET', 'POST'])
    def addingcustom():
        msg = ''
        if session.get('logged_in') == True:
            if request.method == 'POST' and 'challengeName' in request.form and 'shortDescription' in request.form and 'SelectDuration' in request.form and 'SelectCategory' in request.form and 'theImpact' in request.form and 'Suggestions' in request.form:
                challengeName = request.form['challengeName']
                shortDescription = request.form['shortDescription']
                SelectDuration = request.form['SelectDuration']
                SelectCategory = request.form['SelectCategory']
                theImpact = request.form['theImpact']
                suggestionsHelp = request.form['Suggestions']

                newChallenge['name'] = challengeName
                newChallenge['description'] = shortDescription 
                newChallenge['duration'] = SelectDuration 
                newChallenge['category'] = SelectCategory 
                newChallenge['impact'] = theImpact 
                newChallenge['suggestions'] = suggestionsHelp  
      
            elif request.method == 'POST':
                #Form is empty
                msg = 'Please enter all informaton for Custom Challenge.'
        
            #return render_template("challenge_pages/custom_challenge.html", msg = msg, newCC = newChallenge)
            return redirect(url_for('chall_pg8'))
        else:
            msg = 'Please login to access user-only content'
            return render_template("login.html", error = msg)
        

     #function for adding challenge
    
    #function for adding challenge - in progress section
    @app.route("/addChallenge", methods = ['POST'])
    def addChallenge():
        if session.get('logged_in') == True:
            if request.method == 'POST':
                added_chall_name = request.form['addChallenge']
                current_user = session['username']
                connection2 = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                                 user='b33b6415873ff5',
                                 password='d1a1b9a1',
                                 db='heroku_1e2700f5b989c0b',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
                with connection2.cursor() as cursor2:
                    cursor2.execute('SELECT progress FROM dashboard WHERE user = %s', (current_user))
                    progress_chall = cursor2.fetchone()
                    upd_progress = progress_chall['progress'] + added_chall_name
                    # print(upd_progress)
                    cursor2.execute('UPDATE dashboard  SET progress =%s WHERE user=%s', (upd_progress,current_user))
                connection2.commit()
                connection2.close()
            return redirect(url_for('dash'))
        else:
            msg = 'Please login to access user-only content'
            return render_template("login.html", error = msg)
        
    #function for adding challenge - save section
    @app.route("/saveChallenge", methods = ['POST'])
    def saveChallenge():
        if session.get('logged_in') == True:
            if request.method == 'POST':
                saved_chall_name = request.form['saveChallenge']
                current_user = session['username']
                connection2 = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                                 user='b33b6415873ff5',
                                 password='d1a1b9a1',
                                 db='heroku_1e2700f5b989c0b',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
                with connection2.cursor() as cursor2:
                    cursor2.execute('SELECT saved FROM dashboard WHERE user = %s', (current_user))
                    saved_chall = cursor2.fetchone()
                    upd_saved = saved_chall['saved'] + saved_chall_name
                    # print(upd_progress)
                    cursor2.execute('UPDATE dashboard  SET saved =%s WHERE user=%s', (upd_saved,current_user))
                connection2.commit()
                connection2.close()
            return redirect(url_for('dash'))
        else:
            msg = 'Please login to access user-only content'
            return render_template("login.html", error = msg)

    #function for adding challenge - save section
    @app.route("/compChallenge", methods = ['POST'])
    def compChallenge():
        if session.get('logged_in') == True:
            if request.method == 'POST':
                comp_chall_name = request.form['compChallenge']
                current_user = session['username']
                connection2 = pymysql.connect(host='us-cdbr-east-02.cleardb.com',
                                 user='b33b6415873ff5',
                                 password='d1a1b9a1',
                                 db='heroku_1e2700f5b989c0b',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
                with connection2.cursor() as cursor2:
                    cursor2.execute('SELECT completed FROM dashboard WHERE user = %s', (current_user))
                    comp_chall = cursor2.fetchone()
                    upd_comp = comp_chall['completed'] + comp_chall_name
                    # print(upd_progress)
                    cursor2.execute('UPDATE dashboard  SET completed =%s WHERE user=%s', (upd_comp,current_user))
                connection2.commit()
                connection2.close()
            return redirect(url_for('dash'))
        else:
            msg = 'Please login to access user-only content'
            return render_template("login.html", error = msg)


    @app.route("/css")
    def css():
        return render_template("static/css/style.css") 
    
    @app.route("/random")
    def rand_chall():
        number = random.randint(1, 6)
        site = "chall_pg" + str(number)
        return redirect(url_for(site))
        
    def getUserName(name):
        for uType in Users:
            for user in Users[uType]:
                if user['name'] == name:
                    return user['username']
        return None

    def getProfilePic(name):
        for uType in Users:
            for user in Users[uType]:
                if user['name'] == name:
                    return user['profilePic']
        return None
   
    @app.route("/addFriend", methods = ['POST'])
    def addFriend():
        if request.method == 'POST':
            name = request.form['notFriend']
            newFriend = {'username': getUserName(name), 'name': name, 'profilePic':  getProfilePic(name)}
            Users['friends'].append(newFriend)
            Users['notFriends'].remove(newFriend)
        return redirect(url_for('friend'))
      
    @app.route("/remFriend", methods = ['POST'])
    def remFriend():
        if request.method == 'POST':
            name = request.form['friend']
            unFriend = {'username': getUserName(name), 'name': name, 'profilePic': getProfilePic(name)}
            Users['notFriends'].append(unFriend)
            Users['friends'].remove(unFriend)
        return redirect(url_for('friend'))
    
    return app
