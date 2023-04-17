from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import publishTimeoutException
from AWSIoTPythonSDK.core.protocol.internal.defaults import DEFAULT_OPERATION_TIMEOUT_SEC
import datetime
import json
import os
import asyncio
import boto3

from configuration import ConfigurationManager

AWS_IOT = boto3.client('iot')

# Custom MQTT message callback
def custom_callback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")



class MQTTClient:

    def __init__(self):
        self.create_thing()
        self.create_certificate()
        self._client = self.create_client()


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
    
    def create_certificate(self):
        resp = AWS_IOT.create_keys_and_certificate(setAsActive=True)
        data = json.loads(json.dumps(resp, sort_keys=False, indent=4))
        for element in data:
            if element == 'certificateArn':
                cert_arn = data['certificateArn']
            if element == 'keyPair':
                key_pair = data['keyPair']
        with open(f'{self._config.certPath}/{self._taxi_id}.public.key', 'w+') as pubkey_file:
            pubkey_file.write(key_pair['PublicKey'])
        with open(f'{self._config.certPath}/{self._taxi_id}.private.key', 'w+') as prikey_file:
            prikey_file.write(key_pair['PrivateKey'])
        with open(f'{self._config.certPath}/{self._taxi_id}.pem', 'w+') as cert_file:
            cert_file.write(data['certificatePem'])

        resp = AWS_IOT.attach_policy(
            policyName=self._config.policyName,
            target=cert_arn
        )
        resp = AWS_IOT.attach_thing_principal(
            thingName=self._taxi_id,
            principal=cert_arn
        )
    
    def create_thing(self):
        resp = AWS_IOT.create_thing(
            thingName=self._taxi_id,
            thingTypeName=self._config.thingType
        )
        resp = AWS_IOT.add_thing_to_thing_group(
            thingName=self._taxi_id,
            thingGroupName=self._config.thingGroup
        )

    def create_client(self):
        # Init AWSIoTMQTTClient
        myAWSIoTMQTTClient = None
        myAWSIoTMQTTClient = AWSIoTMQTTClient(self._taxi_id)
        myAWSIoTMQTTClient.configureEndpoint(self._config.host, int(self._config.port))
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