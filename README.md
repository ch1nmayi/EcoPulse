## EcoPulse: Where Every Beat Counts Towards Conservation.

Welcome to the EcoPulse! Our project is dedicated to helping commercial buildings optimize their resource usage through sophisticated monitoring and management tools.
By leveraging real-time data collection and analysis, building managers can significantly reduce costs, improve efficiency, and promote sustainability.

## Features

### 1. User Authentication and Management:
- **Registration and Login:** Secure your access through a registration and login system that protects your data with hashed passwords.
- **Session Management:** Keep your session secure and access critical parts of the application, such as the dashboard, settings, or historical data view, only while logged in.

### 2. MySQL Database Integration:
- Our platform uses MySQL to reliably store user information, historical data on electricity and water consumption, and user preferences like alert thresholds.

### 3. Data Tracking and Alerts:
- **Live Data Streaming:** Experience real-time monitoring of electricity and water usage, with an intelligent system that alerts you when consumption exceeds your set thresholds.
- **Alert System:** Get notified promptly without being overwhelmed, thanks to our alert system designed to avoid spamming you with repeated messages.

### 4. Data Visualization and Historical Data:
- **Historical Data Viewing:** Easily access and visualize past consumption data within a selected date range for detailed analysis.
- **Download Data:** Provides the convenience of downloading historical consumption data as CSV files for both electricity and water use.
- **Real-time and Pie Chart Data Streaming:** Not only does our platform support live data streaming, but it also dynamically updates real-time charts, including pie charts that illustrate various consumption patterns, making data analysis both comprehensive and intuitive.

### 5. User-configurable Settings:
- Adjust your alert thresholds for electricity and water usage through an easy-to-use settings page, tailoring the system to your specific needs.

### 6. Forms and Data Validation:
- Benefit from secure and validated forms for registration and login, powered by Flask-WTF, to protect and ensure the integrity of your data.

### 7. Security Features:
- **Password Hashing:** We use bcrypt for hashing passwords, adding an extra layer of security to your account.
- **Input Validation:** Our system rigorously validates inputs to prevent SQL injection and other threats, safeguarding your data's integrity.

### 8. Customizable Dashboard:
- Access a personalized dashboard that not only displays the latest consumption data and alerts but also features dynamic real-time charts for an immediate overview of your resource usage.

### 9. Detailed Consumption Analysis:
- Explore detailed electricity and water consumption data, broken down by categories (e.g., lighting, HVAC for electricity; restrooms, landscaping for water), providing a granular view of your usage patterns.

### 10. Chatbot:
- Interact with our chatbot for quick answers to your questions about consumption data, account details, and more, enhancing your user experience.


### Installation
1. Clone the repository to your local machine.
2. Install the necessary Python packages with `pip install -r requirements.txt`.
3. Set up your MySQL database, ensuring you have your credentials ready.
4. Modify the `config.py` file with your database configuration to connect the application to your MySQL instance.

