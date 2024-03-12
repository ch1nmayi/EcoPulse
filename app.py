from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, flash, Response, stream_with_context, make_response
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
import random
import time
from flask import request
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
import json



app = Flask(__name__)


# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'your_secret_key_here'


mysql = MySQL(app)



#for setting threshold and alert 
electricity_data = []
alert_threshold = 31  # threshold for alert
alert_duration = 60  # Seconds
water_alert_threshold = 350  #  threshold for water
last_alert_time = None

def check_for_alerts(current_value, threshold):
    global last_alert_time
    now = datetime.now()
    
    if current_value > threshold:
        if not last_alert_time:
            last_alert_time = now
        elif (now - last_alert_time).seconds >= alert_duration:
            last_alert_time = None
            flash("The value is exceeding the limit!!!!")
            return True
    else:
        last_alert_time = None
    return False



class RegisterForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self,field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user where email=%s",(field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email",validators=[DataRequired(), Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")


#Log in and authentication 
@app.route('/', methods=["GET","POST"])
def index():
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

        # store data into database 
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (name,email,password) VALUES (%s,%s,%s)",(name,email,hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))

    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE email=%s",(email,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Login failed. Please check your email and password")
            return redirect(url_for('login'))

    return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login'))

#Dash board routing 
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    electricity_data_formatted = []
    water_data_formatted = []

    if request.method == 'POST':
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        with mysql.connection.cursor() as cursor:
            cursor.execute("""SELECT * FROM historical_data 
                            WHERE user_id=%s AND type='electricity' 
                            AND time BETWEEN %s AND %s
                            ORDER BY time DESC""", (user_id, start_date, end_date))
            electricity_data = cursor.fetchall()

            cursor.execute("""SELECT * FROM historical_data 
                            WHERE user_id=%s AND type='water' 
                            AND time BETWEEN %s AND %s
                            ORDER BY time DESC""", (user_id, start_date, end_date))
            water_data = cursor.fetchall()

            # Assuming indices: 0 - ID, 1 - user_id, 2 - value, 3 - data_type, 4 - timestamp
            electricity_data_formatted = [{'time': row[4].strftime('%Y-%m-%d %H:%M:%S'), 'value': row[3]} for row in electricity_data]
            water_data_formatted = [{'time': row[4].strftime('%Y-%m-%d %H:%M:%S'), 'value': row[3]} for row in water_data]

    # Fetch user information for initial GET request or keep after POST
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user WHERE id=%s", (user_id,))
        user = cursor.fetchone()

    return render_template('dashboard.html', user=user, electricity_data=electricity_data_formatted, water_data=water_data_formatted)

def generate_random_data_electricity():
    while True:
        kWh = 28 + random.random() * 4
        now = datetime.now()
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO historical_data (type, value, time) VALUES (%s, %s, %s)", ('electricity', kWh, now))
        mysql.connection.commit()
        cursor.close()
        json_data = json.dumps({
            'time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'value': kWh,
            'alert': check_for_alerts(kWh, alert_threshold),
        })
        yield f"data:{json_data}\n\n"
        time.sleep(1)


def generate_random_data_water():
    while True:
        liters = 300 + random.random() * 100
        now = datetime.now()
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO historical_data (type, value, time) VALUES (%s, %s, %s)", ('water', liters, now))
        mysql.connection.commit()
        cursor.close()
        json_data = json.dumps({
            'time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'value': liters,
            'alert': check_for_alerts(liters, alert_threshold),
        })
        yield f"data:{json_data}\n\n"
        time.sleep(1)




@app.route('/chart-data')
def chart_data():
    return Response(stream_with_context(generate_random_data_electricity()), mimetype="text/event-stream")

@app.route('/chart-data2')
def chart_data2():
    return Response(stream_with_context(generate_random_data_water()), mimetype="text/event-stream")


@app.route('/pie-chart-data')
def pie_chart_data():
    def generate_pie_data():
        while True:
            json_data = json.dumps({
                'data': [
                    28 + random.random() * 4,  # Electricity
                    300 + random.random() * 100,  # Water
                   
                ]
            })
            yield f"data:{json_data}\n\n"
            time.sleep(3600)  # Update every hour to reflect daily changes more realistically

    return Response(stream_with_context(generate_pie_data()), mimetype="text/event-stream")

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        electricity_threshold = request.form['electricity_threshold']
        water_threshold = request.form['water_threshold']
        
        cursor.execute("""UPDATE user SET electricity_threshold=%s, water_threshold=%s WHERE id=%s""",
                       (electricity_threshold, water_threshold, user_id))
        mysql.connection.commit()
        flash('Threshold settings updated successfully.')
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT electricity_threshold, water_threshold FROM user WHERE id=%s", (user_id,))
    thresholds = cursor.fetchone()
    cursor.close()
    return render_template('settings.html', thresholds=thresholds)


if __name__ == '__main__':
    app.run(debug=True)
