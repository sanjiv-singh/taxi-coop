#!/bin/bash

# Description: This script deletes the AWS resources created by the setup.sh script.

iot_registration_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration'
iot_logging_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTLogging'
iot_rule_actions_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions'
docdb_policy_arn='arn:aws:iam::aws:policy/AmazonDocDBFullAccess'

echo "Detaching policies from role..."
aws iam detach-role-policy \
	--role-name Taxi_role \
	--policy-arn $iot_registration_policy_arn

aws iam detach-role-policy \
	--role-name Taxi_role \
	--policy-arn $iot_logging_policy_arn

aws iam detach-role-policy \
	--role-name Taxi_role \
	--policy-arn $iot_rule_actions_policy_arn

aws iam detach-role-policy \
	--role-name Taxi_role \
	--policy-arn $docdb_policy_arn

echo "Deleting IAM role..."
aws iam delete-role \
	--role-name Taxi_role

echo "Deleting IoT thing group..."
aws iot delete-thing-group \
	--thing-group-name Taxi_group

echo "Deleting IoT policy..."
aws iot delete-policy \
	--policy-name Taxi_policy
echo "done"
