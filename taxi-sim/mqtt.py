from AWSIoTPythonSDK.exception.AWSIoTExceptions import publishTimeoutException
from AWSIoTPythonSDK.core.protocol.internal.defaults import DEFAULT_OPERATION_TIMEOUT_SEC
import datetime
import json
import random
import time
import sched

from configuration import configure


PublishRate = 1

# Custom MQTT message callback
def custom_callback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")



class MQTTClient:

    def __init__(self):
        self._client, self._taxi_id, self._topic, self._mode = configure()
        self._lat = 13.0
        self._lng = 75.8


    def publish_data(self, loopCount):
        message = {}
        message['taxi_id'] = self._taxi_id  # 'TAXI_1'
        self._lat += random.uniform(-0.5, 0.5)
        self._lng += random.uniform(-0.5, 0.5)
        try:
            if loopCount % PublishRate == 0:
                location = {'lat': self._lat, 'lng': self._lng}
                timestamp = str(datetime.datetime.now())
                message['timestamp'] = timestamp
                message['location'] = location
                messageJson = json.dumps(message)
                self._client.publish(self._topic, messageJson, 1)

            if self._mode == 'publish':
                print('Published topic %s: %s\n' % (self._topic, messageJson))

        except publishTimeoutException:
            print("Unstable connection detected. Wait for {} seconds. No data is pushed on IoT core from {} to {}.".format(
                DEFAULT_OPERATION_TIMEOUT_SEC, (datetime.datetime.now() - datetime.timedelta(seconds=DEFAULT_OPERATION_TIMEOUT_SEC)), datetime.datetime.now()))


    def connect(self):
        # Connect and subscribe to AWS IoT
        self._client.connect()

        if self._mode == 'both' or self._mode == 'subscribe':
            self._client.subscribe(self._topic, 1, custom_callback)
        time.sleep(2)

    def main_loop(self):
        # Publish to the same topic in a loop forever
        loopCount = 0

        scheduler = sched.scheduler(time.time, time.sleep)

        now = time.time()
        while True:
            try:
                if self._mode == 'both' or self._mode == 'publish':
                    scheduler.enterabs(
                        now+loopCount, 1, self.publish_data, (loopCount,))
                    loopCount += 1
                    scheduler.run()
            except KeyboardInterrupt:
                break

        print("Intiate the connection closing process from AWS.")
        self._client.disconnect()
        print("Connection closed.")
