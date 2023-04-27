#!/bin/bash


# Install Python3 and reuired python packages
echo "Installing Python3 and required packages"
sudo apt-get install -y python3
sudo apt-get install -y python3-pip
sudo apt-get install -y python3-pymongo
sudo pip3 install --upgrade pip
sudo pip3 install boto3 AWSIoTPythonSDK awsiotsdk

# Install AWS CLI
echo "Installing AWS CLI"
sudo apt-get install -y awscli
sudo apt-get install -y aws-sam-cli

# Install MongoDB
echo "Installing MongoDB"
sudo apt-get install gnupg
curl -fsSL https://pgp.mongodb.com/server-6.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg \
   --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | \
	sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org


# Configure AWS CLI
echo "Configuring AWS CLI"
aws configure --profile default
