# import bcrypt

import subprocess
from flask import Flask, render_template, request, redirect, url_for, send_file,session,flash
from werkzeug.utils import secure_filename
from datetime import timedelta
from pymongo import MongoClient
import re
import base64
from bson.objectid import ObjectId
import os
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory,flash,send_file,jsonify
from werkzeug.utils import secure_filename
import unirest

# dictionary for image paths
d={"P1":'img/men1.jpg', "P2":'img/women1.jpg',"P3":'img/men2.jpg',"P4":'img/men3.jpg',"P5":'img/women2.jpg',"P6":'img/men4.jpg',"P7":'img/women3.jpg',"P8":'img/women4.jpg',"P9":'img/men5.jpg'}

# Initialize the Flask application
app = Flask(__name__ )
Client=MongoClient()
db=Client["HCIdb"]


# collect data from db

def get_data():

    if "User_feedback" in db.collection_names():
        userimg = db['User_feedback'].find({})
        # print userimg
        li=[]
        for usr in userimg:
            # print usr
            dict={}
            dict['productname']=usr['productname']
            if "positivecount" in usr:
                dict['positivecount']=usr['positivecount']
            else:
                dict['positivecount']=0

            if "negativecount" in usr:
                dict['negativecount']=usr['negativecount']
            else:
                dict['negativecount']=0

            dict['price']=usr['price']
            dict['total']=dict['negativecount']+dict['positivecount']
            li.append(dict)

        # print li
    return li



@app.before_request
def make_session_permanent():
    # session will remain valid even if the browser is closed
    session.permanent = True
    # session will remain valid till 10 minutes
    app.permanent_session_lifetime = timedelta(minutes=10)
    # app.permanent_session_lifetime = timedelta(seconds=10)



@app.route('/')
def index():
    if 'username' in session:
        if session['username']=="admin":
            return render_template('admin.html')
        else:
            return render_template('home.html')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    uname=request.form.get('username')
    if "Users" in db.collection_names():
        users=db["Users"]
        login_user = users.find_one({'username': request.form['username']})
        # if login_user:
        #     if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == \
        #             login_user[
        #                 'password'].encode('utf-8'):
        if login_user:
            if request.form['pass'].encode('utf-8') == login_user['password'].encode('utf-8'):
                session['username'] = request.form['username']

                session['user_id'] = str(login_user['_id'])

                return redirect(url_for('index'))

    flash('Invalid username/password combination')
    return redirect(url_for('index'),code=302)

@app.route('/submitfeedback', methods=['POST'])
def feedback():

    uploaded_files = request.files.getlist("file[]")
    product_name=request.form.get('product_name')
    print product_name
    comment=request.form.get('comment')
    print comment
    username = session['username']
    print username
    if product_name=="P1":
        price=250
    elif product_name=="P2":
        price=650
    elif product_name=="P3":
        price=1000
    elif product_name=="P4":
        price=200
    elif product_name=="P5":
        price=150
    elif product_name=="P6":
        price=400
    elif product_name=="P7":
        price=750
    elif product_name=="P8":
        price=786
    elif product_name=="P9":
        price=110

    # prediction model call
    ## Generate a key for API first then only this request can be made
    response = unirest.post("https://twinword-sentiment-analysis.p.mashape.com/analyze/",
        headers={
            "X-Mashape-Key": "YourKey",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        },
            params={
            "text": comment
        }
    )

    print response.body['type']
    feedback_senti=response.body['type']

    if "User_feedback" in db.collection_names():
        userimg = db['User_feedback']
    else:
        db.create_collection("User_feedback")
    user = db.User_feedback.find({'productname':product_name }).count()
    print user
    if user!=0:

        if feedback_senti=="positive":
            db.User_feedback.update(
            {"productname": product_name},
            {"$push": {"feedbacksection": {username: comment, "feedback_senti": feedback_senti}},
            "$inc": {"positivecount": 1}
             }
            )
        elif feedback_senti=="negative":
            db.User_feedback.update(
                {"productname": product_name},
                {"$push": {"feedbacksection": {username: comment, "feedback_senti": feedback_senti}},
                "$inc": {"negativecount": 1}
                 })
    elif user==0:

        if feedback_senti == "positive":
            db.User_feedback.insert(
            {
                "productname": product_name,
                "feedbacksection": [],
                "positivecount": 1,
                "price": price

            })
            db.User_feedback.update(
            {"productname": product_name},
            {"$push": {"feedbacksection": {username: comment, "feedback_senti": response.body['type']}}}
             )
        elif feedback_senti == "negative":
            db.User_feedback.insert(
                {
                    "productname": product_name,
                    "feedbacksection": [],
                    "negativecount": 1,
                    "price": price

                })
            db.User_feedback.update(
                {"productname": product_name},
                {"$push": {"feedbacksection": {username: comment, "feedback_senti": response.body['type']}}}
            )
    # Check if the file is one of the allowed types/extensions


    return render_template('home.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['pass'].strip()
        if not username or not password:

            flash("Please enter all the fields.")
            return redirect(url_for('register'), code=302)

        elif not is_username_valid(username):
            flash("Please enter a valid username and password")
            return redirect(url_for('register'))
        elif not is_password_valid(password):
            flash("Please enter a valid username and password")
            return redirect(url_for('register'))
        else:
            users = db["Users"]
            existing_user = users.find_one({'username': username})

            if existing_user is None:

                # hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                # user_detail = users.insert({'username': username, 'password': hashpass})
                user_detail = users.insert({'username': username, 'password': password})


                return redirect(url_for('index'))

            return 'That username already exists!'

    return render_template('register.html')


@app.route('/logout', methods=['POST'])
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   session.pop('user_id',None)
   return redirect(url_for('index'))

@app.route("/data")
def data():
    return jsonify(get_data())

@app.route("/pdata")
def pdata():
    newlist = sorted(get_data(), key=lambda k: k['total'],reverse=True) 
    return jsonify(newlist)

@app.route("/rdata")
def rdata():
    newlist = sorted(get_data(), key=lambda k: k['positivecount'],reverse=True) 
    return jsonify(newlist)



def is_username_valid(username):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9]+$", username):
        return False
    return True
def is_password_valid(password):
    """Validate the email address using a regex."""
    if not re.match("^[a-zA-Z0-9]+$", password):
        return False
    return True

# Generate a user key for S3 Object
# app.secret_key = 'our S3 Key'

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True)