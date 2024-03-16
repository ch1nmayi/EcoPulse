from datetime import datetime
from flask import (
    Flask,
    render_template,
    redirect,
    url_for,
    session,
    flash,
    Response,
    stream_with_context,
    make_response,
    request,
    jsonify,
)
from flask_mysqldb import MySQL
from flask_wtf import FlaskForm
import random
import time
import json
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import bcrypt
import csv
from io import StringIO

faq_data = [
        {
            "tag": "greeting",
            "patterns": ["Hi", "Hello", "How are you?"],
            "responses": ["Hello!", "Hi there!", "Hello, how can I assist you?"]
        },
        {
            "tag": "goodbye",
            "patterns": ["Bye", "See you later", "Goodbye"],
            "responses": ["Goodbye!", "See you later!", "Bye! Have a great day!"]
        },
        {
            "tag": "monitor_resources",
            "patterns": ["What resources can you monitor?", "Which resources are monitored by the system?", "Tell me about resource monitoring."],
            "responses": ["Our system can monitor essential resources such as water and electricity usage.", "We monitor resources like water and electricity consumption.", "We keep track of water and electricity usage among others."]
        },

        {
                "tag": "resource_filters",
                "patterns": ["How can I filter resource data?", "Tell me about resource data filtering.", "Can I filter resource information?"],
                "responses": ["You can filter resource data by specifying dates or types of resources.", "Our system allows you to filter resource data based on dates or specific resource types.", "You have the option to filter resource data by date range or resource category."]
        },
        {
                "tag": "resource_usage",
                "patterns": ["How can I check where certain resources are used more?", "Can I see which resources are consumed the most?", "Tell me about resource usage analysis."],
                "responses": ["Our system provides insights into where certain resources are used more frequently.", "You can analyze resource consumption patterns to see where certain resources are utilized most.", "We offer resource usage analytics to identify areas where certain resources are used more intensively."]
        },
        {   
                 "tag": "resource_alerts",
                 "patterns": ["Do you provide alerts for resource overuse?", "How can I get alerts for resource consumption?", "Tell me about resource overuse notifications."],
                 "responses": ["We offer alerts to notify you about resource overuse.", "You'll receive notifications when there's excessive consumption of resources.", "Our system alerts you when resource usage surpasses certain thresholds."]

        },
        {
            "tag": "blogs",
            "patterns": ["Do you have any blogs?", "Where can I find blogs on your platform?", "Tell me about your blogs."],
            "responses": ["Yes, we have blogs covering various topics related to resource management and conservation.", "You can find informative blogs on our platform covering a wide range of topics.", "Explore our blog section for insightful articles on resource management and related subjects."]
        },
        {
            "tag": "helpline_numbers",
            "patterns": ["Can I get helpline numbers?", "Where can I find helpline numbers?", "Tell me about the helpline support."],
            "responses": ["We provide helpline numbers for assistance with any issues or queries you may have.", "You can access helpline numbers for immediate support and assistance.", "Our helpline support is available to address your concerns and provide guidance."]
        },
        {
            "tag": "contacts",
            "patterns": ["How can I contact support?", "Where can I find contact information?", "Tell me about contacting support."],
            "responses": ["You can contact our support team through the provided contact information.", "Reach out to our support team via the contact details available on our platform.", "Contacting support is easy, just use the provided contact information."]
        },
        {
            "tag": "resource_data_specific_date",
            "patterns": ["How can I find data for a specific date?", "Can I access resource data for a particular day?", "Tell me about finding data for a specific date."],
            "responses": ["You can retrieve resource data for a specific date by specifying the date in the search criteria.", "Specify the date you're interested in to access resource data for that particular day.", "Use our search feature to find resource data for any specific date."]
        },
        {
            "tag": "resource_data_type",
            "patterns": ["How can I find data for a specific resource type?", "Can I filter data by resource category?", "Tell me about accessing data for a particular resource type."],
            "responses": ["You can filter resource data by specifying the type of resource you're interested in.", "Select the resource category you want to analyze to access relevant data.", "Our system allows you to filter data based on resource types for detailed analysis."]
        },
        {
            "tag": "resource_usage_insights",
            "patterns": ["How can I get insights into resource usage?", "Can I analyze resource consumption patterns?", "Tell me about resource usage insights."],
            "responses": ["Our system provides detailed insights into resource usage patterns for informed decision-making.", "Analyze resource consumption trends to gain valuable insights into usage patterns.", "Explore resource usage insights to optimize resource management strategies."]
        },
        {
            "tag": "alert_thresholds",
            "patterns": ["Can I customize alert thresholds?", "How flexible are the alert settings?", "Tell me about setting alert thresholds."],
            "responses": ["You have the flexibility to customize alert thresholds based on your specific requirements.", "Customize alert thresholds to suit your resource management goals and preferences.", "Our system allows you to set personalized alert thresholds according to your needs."]
        },
        {
            "tag": "blog_topics",
            "patterns": ["What topics are covered in your blogs?", "Can you provide examples of blog topics?", "Tell me about the subjects of your blogs."],
            "responses": ["Our blogs cover a wide range of topics including resource conservation techniques, sustainable practices, industry insights, and more.", "Explore blogs on topics such as energy efficiency, water conservation, sustainability initiatives, and technological advancements in resource management.", "Discover informative blogs covering topics like environmental conservation, renewable energy, waste management, and much more."]
        },
        {
            "tag": "helpline_support_hours",
            "patterns": ["When is helpline support available?", "What are the helpline support hours?", "Tell me about the availability of helpline support."],
            "responses": ["Helpline support is available during our operating hours for immediate assistance.", "Our helpline support is accessible during business hours to address your queries and concerns.", "You can reach out to helpline support during our specified support hours for prompt assistance."]
        },
        {
            "tag": "contact_methods",
            "patterns": ["How can I contact support?", "What are the available contact methods?", "Tell me about the ways to contact support."],
            "responses": ["You can contact support via email, phone, or through our online chat system.", "Reach out to support through email, phone, or by initiating a chat session on our platform.", "Contact support using any of the available methods including email, phone, or live chat."]
        },
        {
            "tag": "resource_data_date_range",
            "patterns": ["Can I view resource data for a specific date range?", "How do I access data for a period of time?", "Tell me about accessing data for a date range."],
            "responses": ["Specify the date range you're interested in to view resource data over that period.", "You can access resource data for a specific date range by providing the start and end dates in the search criteria.", "Our system allows you to analyze resource data within a specified date range for comprehensive insights."]
        }
 
            # Add more FAQ data here
        ]

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
electricity_alert_threshold = 300  # threshold for alert
alert_duration = 20 # Seconds
water_alert_threshold = 3000 # threshold for water
last_alert_time = None

def check_for_alerts(current_value, threshold):
    global last_alert_time
    now = datetime.now()
    
    if current_value > threshold:
        if not last_alert_time:
            last_alert_time = now
        elif (now - last_alert_time).seconds >= alert_duration:
            last_alert_time = None
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
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    alerts = []  # Initialize an empty list for alerts
    current_electricity_usage = 0
    current_water_usage = 0


    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user WHERE id=%s", (user_id,))
        user = cursor.fetchone()

        cursor.execute("""SELECT value FROM historical_data 
                          WHERE type = 'electricity' 
                          ORDER BY time DESC LIMIT 1""")
        electricity_data = cursor.fetchone()
        if electricity_data:
            current_electricity_usage = electricity_data[0]
            if check_for_alerts(current_electricity_usage, user[4]): 
                alerts.append("Electricity usage threshold exceeded.")

        cursor.execute("""SELECT value FROM historical_data 
                          WHERE type = 'water' 
                          ORDER BY time DESC LIMIT 1""")
        water_data = cursor.fetchone()
        if water_data:
            current_water_usage = water_data[0]
            if check_for_alerts(current_water_usage, user[5]): 
                alerts.append("Water usage threshold exceeded.")

    return render_template('dashboard.html', user=user, alerts=alerts, current_electricity_usage=current_electricity_usage, current_water_usage=current_water_usage)


def generate_random_data_electricity():
    while True:
        
        kWh = 216 + (random.random() * 1.5)  # the revised equation for daily kWh consumption might look like this
        electricity_anomaly_factor = 10  # Simulating a day with 10x normal usage

        # Applying anomaly under certain conditions
        # Let's assume the anomaly happens with a 10% chance
        if random.random() < 0.3:
            kWh *= electricity_anomaly_factor

        now = datetime.now()
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO historical_data (type, value, time) VALUES (%s, %s, %s)", ('electricity', kWh, now))
        mysql.connection.commit()
        cursor.close()
        alert_flag = check_for_alerts(kWh, electricity_alert_threshold)
        json_data = json.dumps({
            'label': 'Electricity',
            'time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'value': kWh,
            'alert': alert_flag,
        })

        yield f"data:{json_data}\n\n"
        time.sleep(10) #every 10 or whatever seconds we set her will be == 1 day 


def generate_random_data_water():
    while True:
       
        liters = 8670 + (random.random() * 100) # Simplified formula for 1-minute water consumption.
        water_anomaly_factor = 2  # Doubling the normal usage due to a leak
        if random.random() < 0.3:
            liters *= water_anomaly_factor

        now = datetime.now()
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO historical_data (type, value, time) VALUES (%s, %s, %s)", ('water', liters, now))
        mysql.connection.commit()
        cursor.close()
        alert_flag = check_for_alerts(liters, water_alert_threshold)
        json_data = json.dumps({
            'label': 'Water',
            'time': now.strftime('%Y-%m-%d %H:%M:%S'),
            'value': liters,
            'alert':alert_flag ,
        })
        yield f"data:{json_data}\n\n"
        time.sleep(10) #every 10 or whatever seconds we set her will be == 1 day 



@app.route('/history', methods=['GET', 'POST'])
def historical_data():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # If it's a GET request, just render the form template.
    if request.method == 'GET':
        return render_template('history.html')

    # For POST request, process the form data and fetch historical data.
    if request.method == 'POST':
        user_id = session['user_id']
        # Ensure you're getting JSON data correctly.
        data = request.get_json()
        start_date = data['start_date']
        end_date = data['end_date']

        # Initialize response data structure
        response_data = {
            'electricity': {'labels': [], 'data': []},
            'water': {'labels': [], 'data': []}
        }

        with mysql.connection.cursor() as cursor:
            #fetching electricity data
            cursor.execute("""SELECT time, value FROM historical_data 
                            WHERE user_id=%s AND type='electricity' 
                            AND time BETWEEN %s AND %s
                            ORDER BY time DESC""", (user_id, start_date, end_date))
            electricity_data = cursor.fetchall()

            #fetching water data
            cursor.execute("""SELECT time, value FROM historical_data 
                            WHERE user_id=%s AND type='water' 
                            AND time BETWEEN %s AND %s
                            ORDER BY time DESC""", (user_id, start_date, end_date))
            water_data = cursor.fetchall()

        # Adjust date formatting as necessary
        for row in electricity_data:
            date_str = row[0].strftime('%Y-%m-%d') # Format date as string
            response_data['electricity']['labels'].append(date_str)
            response_data['electricity']['data'].append(row[1])

        for row in water_data:
            date_str = row[0].strftime('%Y-%m-%d') # Format date as string
            response_data['water']['labels'].append(date_str)
            response_data['water']['data'].append(row[1])

        return jsonify(response_data)

@app.route('/download-csv')
def download_csv():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = session.get('user_id')
    
    

    si = StringIO()
    cw = csv.writer(si)

    # Write CSV headers
    cw.writerow(['Date', 'Electricity Usage (kWh)', 'Water Usage (Liters)'])

    with mysql.connection.cursor() as cursor:
        # Fetch combined electricity and water data within the date range for the logged-in user
        cursor.execute("""SELECT e.time, e.value AS electricity, w.value AS water
                          FROM historical_data AS e
                          JOIN historical_data AS w ON e.time = w.time AND e.user_id = w.user_id
                          WHERE e.type = 'electricity' AND w.type = 'water'
                          AND e.user_id = %s AND e.time BETWEEN %s AND %s
                          ORDER BY e.time ASC""", (user_id, start_date, end_date))

        for row in cursor.fetchall():
            # Format each row data and write to the CSV writer
            date_str = row[0].strftime('%Y-%m-%d %H:%M:%S')
            cw.writerow([date_str, row[1], row[2]])

    response = make_response(si.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=historical_data.csv'
    response.headers["Content-type"] = "text/csv"
    return response


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
                    216 + random.random() * 1.5,  # Electricity
                    8670 + random.random() * 100,  # Water
                   
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
        
        # Execute the update query
        cursor.execute("""UPDATE user SET electricity_threshold=%s, water_threshold=%s WHERE id=%s""",
                       (electricity_threshold, water_threshold, user_id))
        mysql.connection.commit()
        
        # Close the cursor after committing your changes
        cursor.close()
        
        # Since this is an AJAX request, you return a JSON response
        return jsonify({'success': True, 'message': 'Threshold settings updated successfully.'})
    
    # For GET requests, fetch the current settings and render the template as before
    cursor.execute("SELECT electricity_threshold, water_threshold FROM user WHERE id=%s", (user_id,))
    thresholds = cursor.fetchone()
    cursor.close()
    return render_template('settings.html', thresholds=thresholds)
# Adding a new Route for detailed view for electrical consumption 
@app.route('/Detailed_electricity_data')
def Detailed_electricity_data():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT value FROM historical_data WHERE type='electricity' ORDER BY time DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    
    if row:
        kWh_daily = row[0]
    else:
        # If no data found, use a default or throw an error
        #kWh_daily = 216 
        pass

    distribution = {
        "Lighting": 0.30,
        "HVAC": 0.34,
        "Office Equipment": 0.20,
        "Water Heating & Refridgeration": 0.15,
        "Elevators and Escalators": 0.20,
        "Other Electrical Systems": 0.05
    }

    detailed_consumption = {category: kWh_daily * percentage for category, percentage in distribution.items()}
    return jsonify(detailed_consumption)


@app.route('/Detailed_Water_data')
def Detailed_Water_data():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT value FROM historical_data WHERE type='water' ORDER BY time DESC LIMIT 1")
    row = cursor.fetchone()
    cursor.close()
    
    if row:
        liters_daily = row[0]
    else:
        # If no data found, use a default or throw an error
        #kWh_daily = 216 
        pass

    distribution = {
        "Restrooms": 0.40,
        "HVAC": 0.30,
        "landScaping and irrigation": 0.20,
        "Kitchen & Food Service": 0.05,
        "cleaning and maintainance ": 0.10,
        "Drinking Water and Office Use": 0.02,
    }

    detailed_consumption = {category: liters_daily * percentage for category, percentage in distribution.items()}
    return jsonify(detailed_consumption)

@app.route("/eco")
def eco():
    return render_template("eco.html")

@app.route("/get_response" ,methods=['POST'])
def get_response():
    message = request.form.get("message")
    if not message or not message.strip():
        return "Please enter a message"
 
    response = generate_response(message)
    return response

def generate_response(message):
    found_response = False
    for faq_item in faq_data:
        for pattern in faq_item["patterns"]:
            if pattern.lower() in message.lower():
                found_response = True
                return random.choice(faq_item["responses"])
    if not found_response:
        return "I'm sorry, I don't have an answer to that question."




if __name__ == '__main__':
    app.run(debug=True)
