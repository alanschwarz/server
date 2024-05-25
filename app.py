from flask import Flask, render_template
from flask_socketio import SocketIO
from time import sleep
import RPi.GPIO as GPIO
from hx711 import HX711

import paho.mqtt.client as paho

client = paho.Client()
# client.tls_set(tls_version=paho.mqtt.client.ssl.PROTOCOL_TLS)
# client.username_pw_set("username", "password")
client.connect("192.168.50.18", 1883)

GPIO.setmode(GPIO.BCM)

BUTTON_TARE_GPIO = 18
GPIO.setup(BUTTON_TARE_GPIO, GPIO.IN, GPIO.PUD_UP)

hx = HX711(dout_pin=6, pd_sck_pin=5)
hx.zero()
ratio=734.79
tare=236.5
volume=1.835
hx.set_scale_ratio(ratio)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'preexAMD'  # Replace with your own secret key

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def button_tare_pressed_callback(channel):
    print("Tare pressed!")
    handle_tare()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    weight= hx.get_weight_mean(9)
    if weight>-1 and weight<1 :
        density=weight
    else:
        density=(weight-tare)/volume
    print('density is: ')
    print(density)
    socketio.emit('message', str(density))
    # socketio.emit('message', '0.56')

@socketio.on('tare')
def handle_tare(data):
    print('Received tare command')
    hx.zero(readings=30)
    # weight= hx.tare()

@socketio.on('save')
def handle_tare(data):
    print('Received save command')
    weight= hx.get_weight_mean()
    if weight>-1 and weight<1 :
        density=weight
    else:
        density=(weight-tare)/volume
    print('density is: ')
    print(density)
    # save value to MQTT topic
    # weight= 0
    client.publish("dens_amd/value", payload=density, qos=1)

GPIO.add_event_detect(BUTTON_TARE_GPIO, GPIO.FALLING, callback=button_tare_pressed_callback, bouncetime=300)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)
