from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import publishTimeoutException
from AWSIoTPythonSDK.core.protocol.internal.defaults import DEFAULT_OPERATION_TIMEOUT_SEC
import datetime
import json
import asyncio

from configuration import ConfigurationManager


# Custom MQTT message callback
def custom_callback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")



class MQTTClient:

    def __init__(self):

        config_manager = ConfigurationManager()
        self._client = config_manager.create_client()


    async def publish_data(self):
        try:
            timestamp = str(datetime.datetime.now())
            message = self.get_data()
            message['timestamp'] = timestamp
            messageJson = json.dumps(message)
            self._client.publish(self._topic, messageJson, 1)
            print('Published topic %s: %s\n' % (self._topic, messageJson))

        except publishTimeoutException:
            print("Unstable connection detected. Wait for {} seconds. No data is pushed on IoT core from {} to {}.".format(
                DEFAULT_OPERATION_TIMEOUT_SEC, (datetime.datetime.now() - datetime.timedelta(seconds=DEFAULT_OPERATION_TIMEOUT_SEC)), datetime.datetime.now()))


    def _connect(self):
        # Connect to AWS IoT
        self._client.connect()
    
    def _subscribe(self, topic):
        # Subscribe to AWS IoT
        self._client.subscribe(topic, 1, custom_callback)

    async def main_loop(self, delay):
        while True:
            try:
                await asyncio.sleep(delay)
                await self.publish_data()
            except KeyboardInterrupt:
                break

        print("Intiate the connection closing process from AWS.")
        self._client.disconnect()
        print("Connection closed.")
