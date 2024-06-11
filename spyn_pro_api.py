from flask import Flask, jsonify, render_template_string, request
import requests
import json
from datetime import datetime, timedelta
import pytz
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
        response = requests.post(login_url, headers=self.headers, data=payload)
        self.accessToken = response.json()['accessToken']
        self.headers['WWW-Authenticate'] = f'{self.accessToken}'

    def fetch_active_classes(self):
        classes_url = f"{self.base_url}/proclass/index?venue_id=9629&page=1&plan_id=&skills=&location=&day=&class_time=&age=&level=&start_time=&end_time=&q=&enrolled_count_from_date=19%20Jun%202023&enrolled_count_end_date=19%20Jun%202023"
        response = requests.get(classes_url, headers=self.headers)
        active_classes = response.json()['class']['active']
        self.class_id_title_map = {class_info['id']: class_info['title'] for class_info in active_classes}

    def fetch_users(self, target_date):
        final_result = []
        ist = pytz.timezone('Asia/Kolkata')
        date_today_ist = target_date.strftime('%d-%m-%Y')
        for class_id, title in self.class_id_title_map.items():
            attendance_url = f'{self.base_url}/proattendance/view?venue_id=9629&date={date_today_ist}&subscription_id=&class_id%5B0%5D={class_id}'
            response = requests.get(attendance_url, headers=self.headers)
            re_usernames = [subscriber['username'] for subscriber in response.json().get('reserve_subscriber', [])]
            pr_usernames = [subscriber['username'] for subscriber in response.json().get('present_subscriber', [])]

            final_result.append({
                'date': date_today_ist,
                'class_title': title,
                'reserved_usernames': re_usernames,
                'present_usernames': pr_usernames,
            })

        return [entry for entry in final_result if entry["reserved_usernames"] or entry["present_usernames"]]

    def get_data(self):
        self.fetch_active_classes()
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.now(ist)
        dates_to_fetch = [today - timedelta(days=1), today, today + timedelta(days=1)]
        data = []
        for date in dates_to_fetch:
            data.extend(self.fetch_users(date))
        return data

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    spyn_pro_api = SpynProAPI('deepanshu09@gmail.com', 'Sagar09@')
    data = spyn_pro_api.get_data()
    return jsonify(data)

@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpynPro Classes Data</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 90%;
            margin: 20px auto;
            background: #fff;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h2 {
            text-align: center;
            margin-bottom: 20px;
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
            color: #333;
        }
        tr:nth-child(even) {
            background-color: #f5f5f5;
        }
        tr:hover {
            background-color: #f0dbdb;
        }
        @media screen and (max-width: 600px) {
            table {
                display: block;
                width: 100%;
                overflow-x: auto;
            }
        }
        .separator {
            margin: 20px 0;
            text-align: center;
            font-weight: bold;
            color: #555;
        }
        th, td {
            border-right: 1px solid #ddd;
        }
        th:last-child, td:last-child {
            border-right: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>SpynPro Classes Data</h2>
        <div id="tablesContainer"></div>
    </div>
    <script>
        function fetchData() {
            fetch('/fetch_data')
                .then(response => response.json())
                .then(data => {
                    const dates = [...new Set(data.map(entry => entry.date))];
                    let html = '';
                    dates.forEach(date => {
                        html += `<div class="separator">Data for ${date}</div>`;
                        html += `<table>
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Class</th>
                                            <th>Reserved Names</th>
                                            <th>Present Names</th>
                                            <th>Count (Reserved + Present)</th>
                                        </tr>
                                    </thead>
                                    <tbody>`;
                        data.filter(entry => entry.date === date).forEach(entry => {
                            html += `<tr>
                                        <td>${entry.date}</td>
                                        <td>${entry.class_title}</td>
                                        <td>${entry.reserved_usernames.join(', ')}</td>
                                        <td>${entry.present_usernames.join(', ')}</td>
                                        <td>${entry.reserved_usernames.length + entry.present_usernames.length}</td>
                                     </tr>`;
                        });
                        html += `</tbody></table>`;
                    });
                    document.getElementById('tablesContainer').innerHTML = html;
                });
        }

        // Fetch data on page load
        fetchData();

        // Refresh data every 1 minute (60,000 milliseconds)
        setInterval(fetchData, 60000);
    </script>
</body>
</html>
""")

if __name__ == '__main__':
    app.run(debug=True)
