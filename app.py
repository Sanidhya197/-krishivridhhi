#from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask import * 
import urllib.request  #for making request to api
import numpy as np
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
import json

crop_recommendation_model_path = 'savedmodel.sav'
crop_recommendation_model = pickle.load(
    open(crop_recommendation_model_path, 'rb'))


model = pickle.load(open('classifier.pkl', 'rb'))
fertilizer = pickle.load(open('fertilizer.pkl', 'rb'))


app = Flask(__name__)

app.secret_key = 'CharmeeGandhi'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '2009'
app.config['MYSQL_DB'] = 'user_database'

mysql = MySQL(app)

# model = pickle.load(open('savedmodel.sav', 'rb'))


@app.route('/')
def home():
    title = 'Krishak Vriddhi-Home'
    return render_template('index.html', title=title)


@app.route('/')
def index():
    if 'email' in session:
        username = session['email']
        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to logout</a></b>"
    return "You are not logged in <br><a href = '/login'></b>" + "click here to login</b></a>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    title = 'Krishak Vriddhi-login'
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM accounts WHERE email = % s AND password = % s', (email, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['email'] = account['email']
            msg=' Logged in successfully !'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect email / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    title = 'Krishak Vriddhi-sign Up'
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'email' in request.form:

        email = request.form['email']
        password = request.form['password']
        rep_password = request.form['psw-repeat']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        # elif not re.match(r'[A-Za-z0-9]+', username):
           # msg = 'Username must contain only characters and numbers !'
        elif password != rep_password:
            msg = 'Both passwords must be same '
        elif not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)',
                           (email, password, rep_password, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('signup.html', msg=msg)


@ app.route('/crop-recommend')
def crop_recommend():
    title = 'Krishak Vriddhi - Crop Recommendation'
    return render_template('crop.html', title=title)


@ app.route('/crop-recommend', methods=['POST'])
def crop_prediction():
    title = 'Krishak Vriddhi - Crop Recommendation'

    if request.method == 'POST':
        N = int(request.form['nitrogen'])
        P = int(request.form['phosphorous'])
        K = int(request.form['pottasium'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        my_prediction = crop_recommendation_model.predict(data)
        final_prediction = my_prediction[0]

        return render_template('crop.html', prediction=final_prediction, title=title)


@app.route('/fertilizer_recommend')
def fertilizer_recommend():
    title = 'Krishak Vriddhi - Fertilizer Recommendation'
    return render_template('fertilizer.html', title=title)


@app.route('/fertilizer_recommend', methods=['POST'])
def fertilizer_prediction():

    title = 'Krishak Vriddhi - Fertilizer Recommendation'
    if request.method == 'POST':
        temp = request.form.get('temp')
        humi = request.form.get('humid')
        mois = request.form.get('mois')
        soil = request.form.get('soil')
        crop = request.form.get('crop')
        nitro = request.form.get('nitro')
        pota = request.form.get('pota')
        phosp = request.form.get('phos')
        data = [int(temp), int(humi), int(mois), int(soil),
                int(crop), int(nitro), int(pota), int(phosp)]

        result = fertilizer.classes_[model.predict([data])]

        return render_template('fertilizer.html', x=format(result))


@app.route('/spraying')
def spraying():
    title = 'Krishak Vriddhi-Spraying'
    return render_template('spraying.html', title=title)


@app.route('/schedule' , methods=['get','post'])
def schedule():
    title = 'Krishak Vriddhi-Schedule'
    return render_template('calendar.html', title=title)


@app.route('/weather')
def weather():
   title = 'Krishak Vriddhi-Weather'
   return render_template('weather.html', title=title)

@app.route('/otherCity',methods=['post','get'])
def otherCity():
    if request.method == 'POST':
        city = request.form.get('CityName')
        
    else:
        city='Delhi'
        
    api= "06f887d390672440e1a79483d9babb5a"
    unit="metric"
    
    #source contains json data fromm api
    source = urllib.request.urlopen("https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api + "&units=" + unit).read()
    list_of_data = json.loads(source) 
    
    data = {
        "country_code": str(list_of_data['sys']['country']),
        "cityName" : str(list_of_data['name']),
        "coordinate": str(list_of_data['coord']['lon']) + ' ' 
                    + str(list_of_data['coord']['lat']),
        "temp": str(list_of_data['main']['temp']) + ' ℃',
        "pressure": str(list_of_data['main']['pressure']),
        "humidity": str(list_of_data['main']['humidity']) + ' %.',
        "weather_current": str(list_of_data['weather'][0]['description']) ,
    
    }
    print(data)
    return render_template('otherCity.html',data=data)
        
    
  


@app.route("/contact",methods=['get','post'])
def contact():
    return render_template('contact.html')

@app.route("/guide",methods=['get','post'])
def guide():
    return render_template('guide.html')


if __name__ == '__main__':
    app.run(debug=True)
