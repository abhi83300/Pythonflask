from flask import Flask,render_template
import psutil
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

socketio = SocketIO(app)

@app.route('/')
def home():
   
    return render_template('my_templete.html')

@app.route('/usage')
def cpu():
    return render_template('cpu_usage1.html')




app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))



@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('get_usage_data')
def send_usage_data():
    # Get real CPU and RAM usage data
    cpu_percent = psutil.cpu_percent(percpu=True)
    ram_percent = psutil.virtual_memory().percent
    socketio.emit('usage_data', {'cpu_usage': cpu_percent, 'ram_usage': ram_percent})


if __name__ == '__main__':
    # app.run(port=5000)
    socketio.run(app, debug=True)

    db.create_all()
