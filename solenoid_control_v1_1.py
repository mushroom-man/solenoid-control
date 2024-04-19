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
MQTT_BROKER = "ip_of_pi4"
MQTT_PORT = 1883
MQTT_TOPIC = "solenoid/valve"

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully.")
        client.subscribe(MQTT_TOPIC)
    else:
        print("Connection failed with error code " + str(rc))

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection. Attempting to reconnect...")
        exponential_backoff_reconnect()

def exponential_backoff_reconnect():
    attempt = 0
    while True:
        jitter = random.uniform(0, 30)  # Up to 30 seconds of random delay
        delay = min(2 ** attempt + jitter, 300)  # Cap the delay at 5 minutes
        print(f"Reconnecting in {delay:.2f} seconds...")
        time.sleep(delay)
        try:
            client.reconnect()
            break  # Break the loop if reconnect is successful
        except:
            attempt += 1  # Increment attempt count and try again

def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    if message == "on":
        GPIO.output(valve_pin, GPIO.HIGH)
    elif message == "off":
        GPIO.output(valve_pin, GPIO.LOW)

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
