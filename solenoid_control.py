import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# GPIO setup
valve_pin = 17  # Change this to the actual GPIO pin you're using
GPIO.setmode(GPIO.BCM)
GPIO.setup(valve_pin, GPIO.OUT)

# MQTT Configuration
MQTT_BROKER = "ip_of_pi4"  # Use the IP address of the Pi 4
MQTT_PORT = 1883
MQTT_SOL_VALVE_TOPIC = "solenoid/valve"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(MQTT_SOL_VALVE_TOPIC)

def on_message(client, userdata, msg):
    message = msg.payload.decode("utf-8")
    if message == "on":
        GPIO.output(valve_pin, GPIO.HIGH)
        print("Solenoid valve opened")
    elif message == "off":
        GPIO.output(valve_pin, GPIO.LOW)
        print("Solenoid valve closed")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\nExiting program")
finally:
    GPIO.cleanup()
    print("GPIO pins cleaned up")
