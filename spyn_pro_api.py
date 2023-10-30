from flask import Flask, jsonify
import requests
import json
from datetime import datetime
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

# Your class code here, with minor modifications
class SpynProAPI:

    def __init__(self, email, password):
        self.base_url = 'https://proapp.spyn.co/api/web/v4'
        self.headers = {
            'User-Agent': 'Apidog/1.0.0 (https://www.apidog.com)',
            'Content-Type': 'application/json'
        }
        self.email = email
        self.password = password
        self.login()
        
    def login(self):
        login_url = f"{self.base_url}/user/login"
        payload = json.dumps({
            "LoginForm": {
                "email": self.email,
                "password": self.password,
                "rememberMe": "1",
                "app_type": "business",
                "vid": None,
                "app_device_info": None
            }
        })
        response = requests.request("POST", login_url, headers=self.headers, data=payload)
        self.accessToken = response.json()['accessToken']
        self.headers['WWW-Authenticate'] = f'{self.accessToken}'
        
    def fetch_active_classes(self):
        classes_url = f"{self.base_url}/proclass/index?venue_id=9629&page=1&plan_id=&skills=&location=&day=&class_time=&age=&level=&start_time=&end_time=&q=&enrolled_count_from_date=19%20Jun%202023&enrolled_count_end_date=19%20Jun%202023"
        response = requests.get(classes_url, headers=self.headers)
        active_classes = response.json()['class']['active']
        self.class_id_title_map = {class_info['id']: class_info['title'] for class_info in active_classes}

    def fetch_users(self):
        final_result = []
        ist = pytz.timezone('Asia/Kolkata')
        date_today_ist = datetime.now(ist).strftime('%d-%m-%Y')
        date_today = date_today_ist  # Adjust the format according to your requirement
        for class_id, title in self.class_id_title_map.items():
            attendance_url = f'{self.base_url}/proattendance/view?venue_id=9629&date={date_today}&subscription_id=&class_id%5B0%5D={class_id}'
            response = requests.get(attendance_url, headers=self.headers)
            re_usernames = [subscriber['username'] for subscriber in response.json()['reserve_subscriber']]
            pr_usernames = [subscriber['username'] for subscriber in response.json()['present_subscriber']]
            
            # Format the response
            final_result.append({
                'date': date_today,
                'class_title': title,
                'reserved_usernames': re_usernames,
                'present_usernames': pr_usernames,
            })

        self.filtered_data = [entry for entry in final_result if entry["reserved_usernames"] or entry["present_usernames"]]
        
    def get_data(self):
        self.fetch_active_classes()
        self.fetch_users()
        return self.filtered_data

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    spyn_pro_api = SpynProAPI('deepanshu09@gmail.com', 'Sagar09@')
    data = spyn_pro_api.get_data()
    return jsonify(data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
