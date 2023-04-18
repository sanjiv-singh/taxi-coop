import logging
import json

AllowedActions = ['both', 'publish', 'subscribe']


class ConfigurationManager:

    def __init__(self, config_file_name: str) -> None:
        self.configure(config_file_name)

    def _load_config(self, file):
        with open(file) as f:
            config = json.loads(f.read())
        return config
    
    def get_configuration(self):
        return self._config


    def configure(self, config_file_name: str):

        self._config = self._load_config(config_file_name)
        #self.host = self._config.get('host')
        self.port = self._config.get('port')
        self.certPath = self._config.get('cert_path')
        self.thingGroup = self._config.get('thing_group')
        self.thingType = self._config.get('thing_type')
        self.topicRoot = self._config.get('topic_root')
        self.policyName = self._config.get('policy_name')
        self.port = self._config.get("port")

        # Configure logging
        logger = logging.getLogger("AWSIoTPythonSDK.core")
        logger.setLevel(logging.ERROR)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)
