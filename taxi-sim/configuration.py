from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import argparse
import logging

AllowedActions = ['both', 'publish', 'subscribe']

class ConfigurationManager:

    def __init__(self) -> None:
        self.parse_arguments()
        self.configure()

    def create_client(self):
        # Init AWSIoTMQTTClient
        myAWSIoTMQTTClient = None
        if self.useWebsocket:
            myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId, useWebsocket=True)
            myAWSIoTMQTTClient.configureEndpoint(self.host, self.port)
            myAWSIoTMQTTClient.configureCredentials(self.rootCAPath)
        else:
            myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientId)
            myAWSIoTMQTTClient.configureEndpoint(self.host, self.port)
            myAWSIoTMQTTClient.configureCredentials(self.rootCAPath, self.privateKeyPath, self.certificatePath)

        # AWSIoTMQTTClient connection configuration
        myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

        return myAWSIoTMQTTClient

    def parse_arguments(self):

        # Read in command-line parameters
        parser = argparse.ArgumentParser()
        parser.add_argument("-e", "--endpoint", action="store", required=True,
                            dest="host", help="Your AWS IoT custom endpoint")
        parser.add_argument("-r", "--rootCA", action="store",
                            required=True, dest="rootCAPath", help="Root CA file path")
        parser.add_argument("-c", "--cert", action="store",
                            dest="certificatePath", help="Certificate file path")
        parser.add_argument("-k", "--key", action="store",
                            dest="privateKeyPath", help="Private key file path")
        parser.add_argument("-p", "--port", action="store",
                            dest="port", type=int, help="Port number override")
        parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                            help="Use MQTT over WebSocket")
        parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="taxiPubSub",
                            help="Targeted client id")

        self.args = parser.parse_args()
        
        if self.args.useWebsocket and self.args.certificatePath and self.args.privateKeyPath:
            parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
            exit(2)

        if not self.args.useWebsocket and (not self.args.certificatePath or not self.args.privateKeyPath):
            parser.error("Missing credentials for authentication.")
            exit(2)

    def configure(self):
        self.host = self.args.host
        self.rootCAPath = self.args.rootCAPath
        self.certificatePath = self.args.certificatePath
        self.privateKeyPath = self.args.privateKeyPath
        self.port = self.args.port
        self.useWebsocket = self.args.useWebsocket
        self.clientId = self.args.clientId

        # Port defaults
        if self.useWebsocket and not self.port:  # When no port override for WebSocket, default to 443
            self.port = 443
        if not self.useWebsocket and not self.port:  # When no port override for non-WebSocket, default to 8883
            self.port = 8883

        # Configure logging
        logger = logging.getLogger("AWSIoTPythonSDK.core")
        logger.setLevel(logging.ERROR)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)
