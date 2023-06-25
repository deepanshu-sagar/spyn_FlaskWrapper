from flask import Flask, render_template, g
from spyn_pro_api import SpynProAPI
import threading
import sched, time
import pickle

app = Flask(__name__)

def periodic(scheduler, interval, action, actionargs=()):
    scheduler.enter(interval, 1, periodic, (scheduler, interval, action, actionargs))
    action(*actionargs)

def save_attendance_data():
    spyn_pro_api = SpynProAPI('deepanshu09@gmail.com', 'Sagar09@')
    spyn_pro_api.fetch_active_classes()
    spyn_pro_api.fetch_users()
    data = spyn_pro_api.filtered_data
    # Saving data to a temporary file
    with open('tmp_data.pkl', 'wb') as f:
        pickle.dump(data, f)

@app.before_first_request
def activate_job():
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(0, 1, periodic, (scheduler, 900, save_attendance_data))  # 900 seconds = 15 min
    t = threading.Thread(target=scheduler.run)
    t.start()

@app.route('/get_attendance')
@app.route('/')
def get_attendance():
    data = []
    try:
        with open('tmp_data.pkl', 'rb') as f:
            data = pickle.load(f)
    except:
        pass
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
