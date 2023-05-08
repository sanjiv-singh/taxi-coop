from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import publishTimeoutException
from AWSIoTPythonSDK.core.protocol.internal.defaults import DEFAULT_OPERATION_TIMEOUT_SEC
import datetime
import json
import os
import asyncio

import boto3

AWS_IOT = boto3.client('iot')

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
        self._iot_endpoint = AWS_IOT.describe_endpoint(
                endpointType='iot:Data-ATS'
        ).get('endpointAddress')
        self._client = self.create_client()


    def _publish_data(self, topic, data):
        try:
            messageJson = json.dumps(data)
            self._client.publish(topic, messageJson, 1)
            #print('Published topic %s: %s\n' % (self._topic, messageJson))
            print('.', end='', flush=True)

        except publishTimeoutException:
            print("Unstable connection detected. Wait for {} seconds. No data is pushed on IoT core from {} to {}.".format(
                DEFAULT_OPERATION_TIMEOUT_SEC, (datetime.datetime.now() - datetime.timedelta(seconds=DEFAULT_OPERATION_TIMEOUT_SEC)), datetime.datetime.now()))


    def _connect(self):
        # Connect to AWS IoT
        self._client.connect()
    
    def _disconnect(self):
        # Disconnect from AWS IoT
        self._client.connect()
    
    def _subscribe(self, topic, callback=custom_callback):
        # Subscribe to AWS IoT topic
        self._client.subscribe(topic, 1, callback)

    def main_loop(self, delay):
        """The main loop of the MQTT client"""
        """Override this method to implement your own logic"""
        pass

        print("Intiate the connection closing process from AWS.")
        self._client.disconnect()
        print("Connection closed.")
    
    def create_client(self):
        # Init AWSIoTMQTTClient
        myAWSIoTMQTTClient = None
        myAWSIoTMQTTClient = AWSIoTMQTTClient(self._taxi_id)
        myAWSIoTMQTTClient.configureEndpoint(self._iot_endpoint, int(self._config.port))
        ca_cert = self.rootCAPath = os.path.join(self._config.certPath, 'AmazonRootCA1.pem')
        private_key = os.path.join(self._config.certPath, f'{self._taxi_id}.private.key')
        cert = os.path.join(self._config.certPath, f'{self._taxi_id}.pem')
        myAWSIoTMQTTClient.configureCredentials(ca_cert, private_key, cert)

        # AWSIoTMQTTClient connection configuration
        myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

        return myAWSIoTMQTTClient
