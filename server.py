from flask import Flask, render_template, redirect, request, session, flash
import re
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
# create a regular expression object that we can use run operations on

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key = 'KeepItSecretKeepItSafe'
bcrypt = Bcrypt(app)
mysql = connectToMySQL('emails')
@app.route('/')
def index():
    return render_template('code.html')

@app.route('/success', methods=['Post'])
def process():
    if len(request.form['email']) < 1:
       flash("Invalid Email Address!") # just pass a string to the flash function
    elif not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid Email Address!")
    else:
        flash(f"Success! Your valid email is {request.form['email']}.") # just pass a string to the flash function
        query = "INSERT INTO new_table (email) VALUES (%(email)s);"
        # put the pw_hash in our data dictionary, NOT the password the user provided
        data = { "email" : request.form['email']}
        result = mysql.query_db(query, data)
        query = "SELECT email FROM new_table;"
        result1 = mysql.query_db(query)
        session['result'] = result1
        return redirect('/success')
    return redirect('/')

@app.route('/success')
def success():
    return render_template('user.html')

@app.route('/createUser', methods=['POST'])
def create():
    # include some logic to validate user input before adding them to the database!
    # create the hash
    pw_hash = bcrypt.generate_password_hash(request.form['password'])  
    print(pw_hash)  
    # prints something like b'$2b$12$sqjyok5RQccl9S6eFLhEPuaRaJCcH3Esl2RWLm/cimMIEnhnLb7iC'
    # be sure you set up your database so it can store password hashes this long (60 characters)
    query = "INSERT INTO emails (email) VALUES (%(email)s);"
    # put the pw_hash in our data dictionary, NOT the password the user provided
    data = { "email" : request.form['email']}
    mysql.query_db(query, data)
    # never render on a post, always redirect!
    return redirect("/")

@app.route('/login', methods=['POST'])
def login():
    # see if the username provided exists in the database
    query = "SELECT * FROM users WHERE username = %(username)s;"
    data = {"username" : request.form["username"]}
    result = mysql.query_db(query, data)
    if result:
        # assuming we only have one user with this username, the user would be first in the list we get back
        # of course, for this approach, we should have some logic to prevent duplicates of usernames when we create users
        # use bcrypt's check_password_hash method, passing the hash from our database and the password from the form
        if bcrypt.check_password_hash(result[0]['password'], request.form['password']):
            # if we get True after checking the password, we may put the user id in session
            session['userid'] = result[0]['id']
            # never render on a post, always redirect!
            return redirect('/success')
    # if we didn't find anything in the database by searching by username or if the passwords don't match,
    # flash an error message and redirect back to a safe route
    flash("You could not be logged in")
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)

