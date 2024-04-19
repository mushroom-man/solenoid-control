import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import random

# GPIO setup
valve_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(valve_pin, GPIO.OUT)
GPIO.output(valve_pin, GPIO.HIGH)  # Assume starting open is safe

# MQTT Configuration
MQTT_BROKER = "192.168.10.172"
MQTT_PORT = 1883
MQTT_TOPIC = "solenoid/valve"

# Creating the client and assigning callbacks
client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to {MQTT_TOPIC}")
    else:
        print("Connection failed")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection. Attempting to reconnect...")
        exponential_backoff_reconnect()

def exponential_backoff_reconnect():
    attempt = 0
    while True:
        jitter = random.uniform(0, 30)
        delay = min(2 ** attempt + jitter, 300)
        print(f"Reconnecting in {delay:.2f} seconds...")
        time.sleep(delay)
        try:
            client.reconnect()
            break
        except:
            attempt += 1

def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()} on topic {msg.topic}")
    message = msg.payload.decode("utf-8")
    if message == "on":
        GPIO.output(valve_pin, GPIO.HIGH)
        print("Solenoid valve opened")
    elif message == "off":
        GPIO.output(valve_pin, GPIO.LOW)
        print("Solenoid valve closed")

def connect_to_broker():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nExiting program")
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")

if __name__ == "__main__":
    try:
        connect_to_broker()
    except Exception as e:
        print("An error occurred during operation:", e)
    finally:
        GPIO.cleanup()
        print("GPIO pins cleaned up")
