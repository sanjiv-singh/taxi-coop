#!/bin/bash

# Description: This script creates the AWS IoT thing type, thing group, and policy for the taxi fleet.

iot_registration_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration'
iot_logging_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTLogging'
iot_rule_actions_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions'
docdb_policy_arn='arn:aws:iam::aws:policy/AmazonDocDBFullAccess'

if [ ! -d .certs ]; then
    mkdir .certs
fi

echo "Creating IoT policy....."
aws iot create-policy \
    --policy-name Taxi_policy \
    --policy-document file://taxi_policy.json

echo "Creating IoT role....."
aws iam create-role \
	--role-name Taxi_role \
	--assume-role-policy-document file://taxi_role.json

echo "Attaching policies to role....."
aws iam attach-role-policy \
	--role-name Taxi_role \
	--policy-arn $iot_registration_policy_arn

aws iam attach-role-policy \
	--role-name Taxi_role \
	--policy-arn $iot_logging_policy_arn

aws iam attach-role-policy \
	--role-name Taxi_role \
	--policy-arn $iot_rule_actions_policy_arn

aws iam attach-role-policy \
	--role-name Taxi_role \
	--policy-arn $docdb_policy_arn

role_arn=$(aws iam get-role --role-name Taxi_role --query Role.Arn --output text)
echo $role_arn > role_arn.txt

echo "Creating IoT thing type....."
type_deprecated=$(aws iot describe-thing-type --thing-type-name TAXI --query thingTypeMetadata.deprecated --output text)

if [ $type_deprecated = "False" ]; then
	echo "Thing type TAXI already exists"
elif [ $type_deprecated = "True" ]; then
	aws iot deprecate-thing-type \
	--thing-type-name TAXI \
	--undo-deprecate
else
	aws iot create-thing-type \
		--thing-type-name TAXI \
		--thing-type-properties "thingTypeDescription=Taxi as an IoT Device"
fi

echo "Creating IoT thing group....."
aws iot create-thing-group \
	--thing-group-name Taxi_group \
	--thing-group-properties "thingGroupDescription=Taxi Group"
echo "done"
