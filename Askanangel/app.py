from flask import Flask, render_template, request, session, redirect, url_for

import sqlite3

app = Flask(__name__)
app.secret_key = 'yourm0m'
DATABASE = 'maindb.db'
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Perform login logic here
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        
        if user:
            
            session['login'] = True
            session['username'] = username
            print(user)
            session['email'] = user[3]
            session['firstname'] = user[4]
            session['lastname'] = user[5]
            session['bio'] = user[6]
            session['country'] = user[7]
            session['city'] = user[8]
            session['type'] = user[9]
            session['balance'] = user[10]
            conn.close()
            return render_template('home.html')
        else:
            conn.close()
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['FirstName']
        surname = request.form['LastName']
        if request.form.get('account_type') == 'angel':
            accountype = 2
        else:
            accountype = 1

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, email, name, surname, accounttype) VALUES (?, ?, ?, ?, ?, ?)",
        (username, password, email, name, surname, accountype))
        
        conn.commit()
        conn.close()
        
        return render_template('login.html')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    # Clear the session variables
    session.clear()

    # Redirect to the login page or any other desired page
    return render_template('login.html')

def getServicesForID(userid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT service FROM services WHERE userid=?", (userid,))
    result = cursor.fetchall()
    print(result)
    print(type(result))
    
    conn.commit()
    conn.close()
    return result
def getHashtagsForID(userid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT keyword FROM keywords WHERE userid=?", (userid,))
    result = cursor.fetchall()
    print(result)
    print(type(result))
    
    conn.commit()
    conn.close()
    return result
@app.route('/profileangel', methods=['GET', 'POST'])
def profileangel():
    username = session['username']
    userid = getIdFromUsername(username)
    
    services = getServicesForID(int(userid))
    hashtags = getHashtagsForID(int(userid))
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        bio = request.form['bio']
        country = request.form['country']
        city = request.form['city']
        
        username = session['username']

        conn = sqlite3.connect('maindb.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET name=?, surname=?, email=?, bio=?, country=?, city=? WHERE username=?", (firstname, lastname, email, bio, country, city, username))
        conn.commit()
        conn.close()
        session['firstname'] = firstname
        session['lastname'] = lastname
        session['email'] = email
        session['bio'] = bio
        session['country'] = country
        session['city'] = city
        return render_template('profileangel.html', username=session['username'], services = services, hashtags=hashtags)
    return render_template('profileangel.html', username=session['username'], services = services, hashtags=hashtags)

@app.route('/addhashtag', methods=['POST'])
def addhashtag():
    if request.method == 'POST':
        username = session['username']
        print(username)
        hashtag = request.form['hashtag']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        result = cursor.fetchall()
        print(result[0][0])
        userid = int(result[0][0])
        print("oktest")
        conn.commit
        conn.close    
        print(userid)
        print(hashtag)    
        addtagtoDB(userid, hashtag)
        return redirect(url_for('profileangel'))
    return redirect(url_for('profileangel'))

def addtagtoDB(id, hashtag):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO keywords (userid,keyword) VALUES (?,?)",
        (id, hashtag))
    conn.commit()
    conn.close()
    print("done")

def getIdFromUsername(username):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    result = cursor.fetchall()
    userid = int(result[0][0])
    conn.commit
    conn.close 
    return userid
@app.route('/addservice', methods=['POST'])
def addservice():
    if request.method == 'POST':
        username = session['username']
        print(username)
        service = request.form['service']
        price = request.form['price']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        result = cursor.fetchall()
        print(result[0][0])
        userid = int(result[0][0])
        print("oktest")
        conn.commit
        conn.close    
        addservicetoDB(userid, service, price)
        return redirect(url_for('profileangel'))
    
    return redirect(url_for('profileangel'))
def addservicetoDB(id, service, price):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO services (userid,service,price) VALUES (?,?,?)",
        (id, service, price))
    conn.commit()
    conn.close()
    print("done")
@app.route('/home', methods=['GET'])
def home():
    if request.method == 'GET':

        return render_template('home.html')
    
@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        searchKeyword = request.form['searchterm']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT userid FROM keywords WHERE keyword=?", (searchKeyword,))
        result1 = cursor.fetchall()
        print(Extract(result1))
        conn.commit()
        conn.close()
        results = getSearchResultsForHashtag(Extract(result1))
        
        return render_template('home.html', results=results, searchKeyword=searchKeyword)
    return render_template('home.html')

def getSearchResultsForHashtag(userid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id IN ({})".format(','.join(['?']*len(userid)))
    cursor.execute(query, userid)
    result = cursor.fetchall()
    print(result)
    conn.commit()
    conn.close()
    print("ok")
    return result
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        bio = request.form['bio']
        country = request.form['country']
        city = request.form['city']
        
        username = session['username']

        conn = sqlite3.connect('maindb.db')
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET name=?, surname=?, email=?, bio=?, country=?, city=? WHERE username=?", (firstname, lastname, email, bio, country, city, username))
        conn.commit()
        conn.close()
        session['firstname'] = firstname
        session['lastname'] = lastname
        session['email'] = email
        session['bio'] = bio
        session['country'] = country
        session['city'] = city
        return render_template('profile.html', username=session['username'])
    return render_template('profile.html', username=session['username'])
def getUserByName(name):
    conn = sqlite3.connect('maindb.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result
def getServicesPriceForID(userid):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM services WHERE userid=?", (userid,))
    result = cursor.fetchall()
    
    conn.commit()
    conn.close()
    return result
@app.route('/viewprofile', methods=['GET'])
def viewprofile():
    user = request.args.get('user')
    
    
    userProf = getUserByName(user)
    print(userProf)
    print(userProf[0])
    services = getServicesPriceForID(userProf[0])
    print(services)
    return render_template('viewprofile.html', userProf=userProf, services=services)
@app.route('/payment', methods=['POST'])
def payment():
    if request.method == 'POST':
        serviceid = request.form['serviceid']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM services WHERE id=?", (serviceid,))
        result = cursor.fetchall()
        print(result)
        conn.commit()
        conn.close()
        return render_template('payment.html', result=result)
    
@app.route('/buy', methods=['POST'])
def buy():
    if request.method == 'POST':
        username = session['username']
        userid = getIdFromUsername(username)
        serviceid = request.form['serviceid']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (userid,serviceid) VALUES (?,?)", (userid, serviceid))
        conn.commit()
        conn.close()
        return render_template('home.html')
    
@app.route('/transactions', methods=['GET'])
def transactions():
    return render_template('transactions.html')
@app.route('/messages', methods=['GET'])
def messages():
    return render_template('messages.html')
def Extract(lst):
    return [item[0] for item in lst]
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
