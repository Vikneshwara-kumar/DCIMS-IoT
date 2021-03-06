#importing libraries
from SimulatedIoT import TempratureSensor
from SimulatedIoT import HumiditySensor
import RPi.GPIO as GPIO
import ssl
import time
from datetime import datetime
import json
import paho.mqtt.client as mqtt


# Connect the Grove PIR Motion Sensor to digital port D8
# SIG,NC,VCC,GND
#defining Physical sensors
pir_sensor = 4
smoke_sensor = 3
GPIO.setmode(GPIO.BCM)
GPIO.setup(pir_sensor, GPIO.IN)
GPIO.setup(smoke_sensor, GPIO.IN)

motion=0
smoke=0
flag = False
i=0
Ts=0
Hs=0

def Sensor_monitor():
    global Smoke, Motion, i, Ts, Hs, inst
    i = i + 1
    inst = "52ks563ks"
    dt = datetime.now().strftime("%d-%m-%YT%H:%M:%S")
    motion = GPIO.input(pir_sensor)
    smoke = GPIO.input(smoke_sensor)

    if motion == 0 or motion == 1:                                          # check if reads were 0 or 1 it can be 255 also because of IO Errors so remove those values
        if motion == 1:
            Motion = "Alarm"
        else:
            Motion = "Normal"

    if smoke == 0 or smoke == 1:                                            # check if reads were 0 or 1 it can be 255 also because of IO Errors so remove those values
        if smoke == 0:
            Smoke = "Alarm"
        else:
            Smoke = "Normal"
    time.sleep(1)
    if i==5:
        ts = TempratureSensor(10, 10, 15, 30)                               #call tempererature function to generate random values
        hs = HumiditySensor(75, 10, 15, 60)                                 #call humidity function to generate random values
        Ts = ts.sense()
        Hs = hs.sense()
        inst = ts.instanceID
        i=0

    message = {
        "Area-id": "Data Center-1",
        "instance-id": inst,
        "timestamp": dt,
        "Temperature": Ts,
        "Humidity": Hs,
        "Motion": Motion,
        "FireAlarm": Smoke
    }
    jmsg = json.dumps(message, indent=4)
    mqtt_publisher.publish("Area-1/Sensor_Data", jmsg, 1)                                   #Topic:Area-1/Sensor_Data to publish for sensor values
    return jmsg
############### MQTT section ##################

# when connecting to mqtt do this;

def on_connect(client, userdata, flags, rc):
    global flag
    print("Connected to AWS")
    flag = True
    print("Connected with result code "+str(rc))

# when receiving a mqtt message do this;

def on_message(client, userdata, msg):
    message = str(msg.payload)
    print(msg.topic+" "+message)


mqtt_publisher = mqtt.Client()
mqtt_publisher.on_connect = on_connect                                                      #assign on_connect function
mqtt_publisher.on_message = on_message                                                      #assign on_message function
awshost = "a1xct602hf98vg-ats.iot.us-east-1.amazonaws.com"                                  #Endpoint
awsport = 8883                                                                              #Port no.

caPath = "/home/pi/DCIMS-IoT/AWSIoT/Root-CA.pem"                                            # Root_CA_Certificate_Name
certPath = "/home/pi/DCIMS-IoT/AWSIoT/certificate.pem.crt"                                  # <Thing_Name>.cert.pem
keyPath = "/home/pi/DCIMS-IoT/AWSIoT/private.pem.key"                                       # <Thing_Name>.private.key

mqtt_publisher.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2,
              ciphers=None)  # pass parameters
mqtt_publisher.username_pw_set("username", "password")
mqtt_publisher.connect(awshost, awsport, keepalive=60)                                      # connect to aws server

mqtt_publisher.loop_start()


while True:
    if flag == True:
        Sensor_monitor()
        print("Just Published " + str(Sensor_monitor()) + " topic Sensor data" )
    else:
        print("waiting for connection....")
