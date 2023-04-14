#!/bin/bash

TAXI_SL_NUM=1

iot_registration_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration'
iot_logging_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTLogging'
iot_role_actions_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions'
dynamodb_policy_arn = 'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'

aws iam create-role --role-name stockprice-ec2-role --assume-role-policy-document file://ec2_policy.json --output text
    aws iam attach-role-policy --role-name stockprice-ec2-role --policy-arn $kinesis_policy_arn

aws iot create-keys-and-certificate \
    --certificate-pem-outfile ".certs/taxi_$TAXI_SL_NUM.cert.pem" \
    --public-key-outfile ".certs/taxi_$TAXI_SL_NUM.public.key" \
    --private-key-outfile ".certs/taxi_$TAXI_SL_NUM.private.key"

