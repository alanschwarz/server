from flask import Flask, render_template
from flask_socketio import SocketIO

import RPi.GPIO as GPIO
from hx711 import HX711

import paho.mqtt.client as paho

client = paho.Client()
# client.tls_set(tls_version=paho.mqtt.client.ssl.PROTOCOL_TLS)
# client.username_pw_set("username", "password")
client.connect("192.168.50.18", 1883)

key1=18
key3=24
GPIO.setmode(GPIO.BCM)
GPIO.setup(key1, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(key3, GPIO.IN, GPIO.PUD_UP)


hx = HX711(dout_pin=6, pd_sck_pin=5)
hx.zero()
ratio=734.79
tare=236.5
volume=1.835
hx.set_scale_ratio(ratio)

density=0
densidad='peso en gramos'
estable=0
promedio=0
lista=[0,0,0]

app = Flask(__name__)
app.config['SECRET_KEY'] = 'preexAMD'  # Replace with your own secret key

socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

#def button_tare_pressed_callback(channel):
#    print("Tare pressed!")
#    handle_tare()

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    weight= hx.get_weight_mean(9)
    global lista
    global density
    global promedio
    global densidad
    global estable
    if weight>-0.2 and weight<tare-0.2 :
        density=weight
        densidad='peso en gramos'
    elif weight>=tare-0.2 and weight <tare +100*volume:
        density=(weight-tare)/volume
        densidad='densidad en gramos/litro'
    else:
        density=-100.0
        densidad='fuera de rango - TARA'
    lista[2]=lista[1]
    lista[1]=lista[0]
    lista[0]=density
    promedio=(lista[1]+lista[0]+lista[2])/3
    if densidad=='densidad en gramos/litro' and abs(lista[0]-promedio)<0.2 and abs(lista[1]-promedio)<0.2 and abs(lista[2]-promedio)<0.2 :
        estable=1
    else:
        estable=0
    print('density is: ')
    print(density)
    socketio.emit('message', {'valor':str(density), 'unidad':densidad,'estable':estable})
    # socketio.emit('message', '0.56')

@socketio.on('tare')
def handle_tare(data):
    print('Received tare command')
    hx.zero(readings=30)
    # weight= hx.tare()

@socketio.on('save')
def handle_save(data):
    print('Received save command')
    if densidad=='densidad en gramos/litro' and estable== :
        dato=promedio
    else:
        dato=0.0
    print('density is: ')
    print(dato)
    # save value to MQTT topic
    # weight= 0
    client.publish("dens_amd/value", payload=dato, qos=1)
    
GPIO.add_event_detect(key1, GPIO.FALLING, callback=handle_tare, bouncetime=300)
GPIO.add_event_detect(key3, GPIO.FALLING, callback=handle_save, bouncetime=300)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)
