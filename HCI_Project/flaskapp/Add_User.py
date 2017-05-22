import os
import json

from flask import Flask, render_template, request, redirect, url_for, send_from_directory,flash,send_file
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import base64
# Initialize the Flask application
app = Flask(__name__)
client = MongoClient('localhost:27017')
db = client.UserData
app.secret_key = 'super secret key'
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('beupload.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded files
    uploaded_files = request.files.getlist("file[]")
    print uploaded_files
    firstname=request.form.get("firstname")
    lastname = request.form.get("lastname")
    emailaddress = request.form.get("emailaddress")
    filenames = []

    list1=[]
    for file in uploaded_files:
        print file
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            print filename
            image_file = open(filename, "r")
            image_filer = image_file.read()
            print image_filer
            encoded_string = base64.b64encode(image_filer)
            print encoded_string
            list1.append(encoded_string)

    db.User_Info.insert_one(
    {
                "firstname": firstname,
                "lastname": lastname,
                "emailaddress": emailaddress,
                "images": list1

    })
        # Check if the file is one of the allowed types/extensions

    flash("Image Uploaded in Database")
    return render_template('beupload.html')

@app.route('/display', methods=['POST'])
def read():
    images=[]
    userInfo = db.User_Info.find({ "firstname":"Tasneem"},{ "firstname":0,"lastname":0, "emailaddress":0,"_id": 0 })
    print '\n All data from EmployeeData Database \n'
    for a in userInfo:
        image=a["images"]
        print image
        for user_img in image:
            print user_img
            print"Hi"
            image_64_decode = user_img.decode()
            images.append(image_64_decode)

            return render_template("displayuser.html",images=images)



if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        debug=True
    )
