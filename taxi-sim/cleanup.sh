#!/bin/bash

# Description: This script deletes the AWS resources created by the setup.sh script.

iot_registration_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration'
iot_logging_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTLogging'
iot_rule_actions_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions'
docdb_policy_arn='arn:aws:iam::aws:policy/AmazonDocDBFullAccess'

policy_name='Taxi_policy'

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

echo "Deleting IoT topic rule..."
aws iot delete-topic-rule \
        --rule-name taxi_iot_lambda_rule

echo "Deleting IoT thing group..."
aws iot delete-thing-group \
	--thing-group-name Taxi_group

echo "Deleting IoT things..."
for thing_name in $(aws iot list-things --query things[].thingName --output text); do

	echo "$thing_name"

	for principal in $(aws iot list-thing-principals --thing-name $thing_name  --query principals --output text); do
		#readarray -d : -t arr1 <<< "$principal"
		#readarray -d : -t arr2 <<< ${arr1[5]}
		#cert_id=${arr2[1]}
		aws iot detach-thing-principal \
			--thing-name $thing_name \
			--principal $principal
		aws iot detach-policy \
			--policy-name $policy_name \
			--target $principal
	done

	aws iot delete-thing \
		--thing-name $thing_name
	rm -f .certs/$thing_name.pem
	rm -f .certs/$thing_name.private.key
	rm -f .certs/$thing_name.public.key
done

echo "Deleting IoT certificates..."
for cert_id in $(aws iot list-certificates --query certificates[].certificateId --output text); do
	aws iot update-certificate --certificate-id $cert_id --new-status INACTIVE
	aws iot delete-certificate --certificate-id $cert_id
done

echo "Deleting IoT policy..."
aws iot delete-policy \
	--policy-name $policy_name
echo "done"
