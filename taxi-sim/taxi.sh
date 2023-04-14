#!/bin/bash

python taxi.py \
	-e a3eiore48b4qfq-ats.iot.us-east-1.amazonaws.com \
	--r setup/.certs/AmazonRootCA1.pem \
	-c setup/.certs/TAXI_1_device.pem \
	-k setup/.certs/TAXI_1_private.key 
