
from mqtt import MQTTClient

client = MQTTClient()
client.connect()
client.main_loop()
