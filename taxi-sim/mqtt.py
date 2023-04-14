from AWSIoTPythonSDK.exception.AWSIoTExceptions import publishTimeoutException
from AWSIoTPythonSDK.core.protocol.internal.defaults import DEFAULT_OPERATION_TIMEOUT_SEC
import datetime
import json
import random
import time
import sched

from configuration import configure


PublishFreqHeartRate = 1
PublishFreqTemperature = 15
PublishFreqOxygen = 10


# Custom MQTT message callback
def custom_callback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")



class MQTTClient:

    def __init__(self):
        self._client, self._deviceId, self._topic, self._mode = configure()


    def publish_data(self, loopCount):
        message = {}
        message['deviceid'] = self._deviceId  # 'TAXI_1'
        try:
            if loopCount % PublishFreqTemperature == 0:
                value = float(random.normalvariate(99, 1.5))
                value = round(value, 1)
                timestamp = str(datetime.datetime.now())
                message['timestamp'] = timestamp
                message['datatype'] = 'Temperature'
                message['value'] = value
                messageJson = json.dumps(message)
                self._client.publish(self._topic, messageJson, 1)

            if loopCount % PublishFreqOxygen == 0:
                value = int(random.normalvariate(90, 3.0))
                timestamp = str(datetime.datetime.now())
                message['timestamp'] = timestamp
                message['datatype'] = 'SPO2'
                message['value'] = value
                messageJson = json.dumps(message)
                self._client.publish(self._topic, messageJson, 1)

            if loopCount % PublishFreqHeartRate == 0:
                value = int(random.normalvariate(85, 12))
                timestamp = str(datetime.datetime.now())
                message['timestamp'] = timestamp
                message['datatype'] = 'HeartRate'
                message['value'] = value
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
