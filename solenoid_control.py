import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import random

# GPIO setup
valve_pin = 17  # Change this to the actual GPIO pin you're using
GPIO.setmode(GPIO.BCM)
GPIO.setup(valve_pin, GPIO.OUT)

# MQTT Configuration
MQTT_BROKER = "ip_of_pi4"  # Use the IP address of the Pi 4
MQTT_PORT = 1883
MQTT_SOL_VALVE_TOPIC = "solenoid/valve"

# Reconnection Parameters
base_delay = 1  # Initial delay in seconds
max_delay = 300  # Maximum delay in seconds
multiplier = 2  # Delay multiplier
attempts = 0  # Attempt counter

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected with result code " + str(rc))
        client.subscribe(MQTT_SOL_VALVE_TOPIC)
        global attempts
        attempts = 0  # Reset attempts after successful reconnection
    else:
        print("Failed to connect, return code %d\n", rc)
        # Initiating reconnection from here might cause a loop, handle with caution

def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    if message == "on":
        GPIO.output(valve_pin, GPIO.HIGH)
        print("Solenoid valve opened")
    elif message == "off":
        GPIO.output(valve_pin, GPIO.LOW)
        print("Solenoid valve closed")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        reconnect()

def reconnect():
    global attempts
    delay = min(base_delay * (multiplier ** attempts), max_delay)
    delay = delay * random.uniform(0.5, 1.5)  # Adding jitter
    time.sleep(delay)
    attempts += 1
    try:
        client.reconnect()
    except:
        print("Reconnection failed, trying again...")
        reconnect()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()  # Using loop_start() for non-blocking loop that will automatically reconnect
    while True:  # Keep the main thread alive
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting program")
finally:
    client.loop_stop()  # Ensure the network loop is stopped
    GPIO.cleanup()
    print("GPIO pins cleaned up")

