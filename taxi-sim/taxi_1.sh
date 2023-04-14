#!/bin/bash

python taxi.py \
	-e a3eiore48b4qfq-ats.iot.us-east-1.amazonaws.com \
	--r setup/.certs/AmazonRootCA1.pem \
	-d TAXI_1 \
	-c setup/.certs/TAXI_1_device.pem \
	-k setup/.certs/TAXI_1_private.key \
	-id taxi_1 \
	-t iot/TAXI/1
