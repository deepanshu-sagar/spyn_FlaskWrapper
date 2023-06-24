from flask import Flask, render_template
from spyn_pro_api import SpynProAPI

app = Flask(__name__)

@app.route('/')
def home():
    spyn_pro_api = SpynProAPI('deepanshu09@gmail.com', 'Sagar09@')
    spyn_pro_api.fetch_active_classes()
    spyn_pro_api.fetch_users()
    data = spyn_pro_api.filtered_data
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
