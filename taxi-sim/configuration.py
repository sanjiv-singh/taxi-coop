from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import argparse
import logging

AllowedActions = ['both', 'publish', 'subscribe']


def parse_arguments():

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
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                        help="Targeted client id")
    parser.add_argument("-d", "--deviceId", action="store", dest="deviceId", default="BSM",
                        help="Device ID")
    parser.add_argument("-t", "--topic", action="store", dest="topic",
                        default="sdk/test/Python", help="Targeted topic")
    parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                        help="Operation modes: %s" % str(AllowedActions))
    parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                        help="Message to publish")

    args = parser.parse_args()
    
    if args.mode not in AllowedActions:
        parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
        exit(2)

    if args.useWebsocket and args.certificatePath and args.privateKeyPath:
        parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
        exit(2)

    if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
        parser.error("Missing credentials for authentication.")
        exit(2)

    return args

def configure():
    args = parse_arguments()
    host = args.host
    rootCAPath = args.rootCAPath
    certificatePath = args.certificatePath
    privateKeyPath = args.privateKeyPath
    port = args.port
    useWebsocket = args.useWebsocket
    clientId = args.clientId
    deviceId = args.deviceId
    topic = args.topic
    mode = args.mode

    # Port defaults
    if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
        port = 443
    if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
        port = 8883

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.ERROR)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    # Init AWSIoTMQTTClient
    myAWSIoTMQTTClient = None
    if useWebsocket:
        myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
        myAWSIoTMQTTClient.configureEndpoint(host, port)
        myAWSIoTMQTTClient.configureCredentials(rootCAPath)
    else:
        myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
        myAWSIoTMQTTClient.configureEndpoint(host, port)
        myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    return myAWSIoTMQTTClient