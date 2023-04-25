#!/bin/bash

# Description: This script creates the AWS IoT thing type, thing group, and policy for the taxi fleet.

if [ -z "$DB_USER" ]; then
	echo "DB_USER is not set"
	echo "Please set the environment variable DB_USER"
	echo "e.g. export DB_USER=taxi"
	exit 1
fi
if [ -z "$DB_PASSWORD" ]; then
	echo "DB_PASSWORD is not set"
	echo "Please set the environment variable DB_PASSWORD"
	echo "e.g. export DB_PASSWORD=taxi"
	exit 1
fi


iot_registration_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration'
iot_logging_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTLogging'
iot_rule_actions_policy_arn='arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions'
docdb_policy_arn='arn:aws:iam::aws:policy/AmazonDocDBFullAccess'

if [ ! -d .certs ]; then
    mkdir .certs
fi
if [ ! -f .certs/AmazonRootCA1.pem ]; then
    wget -O .certs/AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem
fi


create_lambda () {
    lambda_execution_policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    docdb_policy_arn="arn:aws:iam::aws:policy/AmazonDocDBFullAccess"
    iot_policy_arn="arn:aws:iam::aws:policy/AWSIoTFullAccess"
    aws iam create-role --role-name taxi-iot-lambda-role \
        --assume-role-policy-document file://../taxi-db/lambda_policy.json --output text
    aws iam attach-role-policy --role-name taxi-iot-lambda-role \
        --policy-arn $lambda_execution_policy_arn
    aws iam attach-role-policy --role-name taxi-iot-lambda-role \
        --policy-arn $docdb_policy_arn
    aws iam attach-role-policy --role-name taxi-iot-lambda-role \
        --policy-arn $iot_policy_arn
    aws iam put-role-policy \
	    --role-name taxi-iot-lambda-role \
	    --policy-name taxi-lambda-ec2 \
	    --policy-document file://../taxi-db/lambda_ec2_policy.json
    role_arn=$(aws iam get-role --role-name "taxi-iot-lambda-role" \
        --query "Role.Arn" --output text)
    sleep 5

    security_group_ids=""
    for security_group in $(aws ec2 describe-security-groups --query SecurityGroups[].GroupId --output text); do
	if [ -z "$security_group_ids" ]; then
		security_group_ids+=$security_group
	else
		security_group_ids+=","
		security_group_ids+=$security_group
	fi
    done

    subnet_ids=""
    for subnet in $(aws ec2 describe-subnets --query Subnets[].SubnetId --output text); do
	if [ -z "$subnet_ids" ]; then
		subnet_ids+=$subnet
	else
		subnet_ids+=","
		subnet_ids+=$subnet
	fi
    done

    end_point=$(aws docdb describe-db-clusters --query DBClusters[].Endpoint --output text)


    zip -r taxi_iot_lambda_package.zip taxi_iot_lambda.py
    aws lambda create-function \
        --function-name taxi_iot_lambda \
        --runtime python3.9 \
        --environment "Variables={db_user=$DB_USER,db_pass=$DB_PASSWORD,db_endpoint=$end_point}" \
        --zip-file fileb://taxi_iot_lambda_package.zip \
        --handler taxi_iot_lambda.lambda_handler \
        --role $role_arn \
        --vpc-config SubnetIds=$subnet_ids,SecurityGroupIds=$security_group_ids

    aws lambda add-permission \
	--function-name taxi_iot_lambda \
	--statement-id iot-events \
	--action "lambda:InvokeFunction" \
	--principal api.amazonaws.com

}


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

echo "Creating lambda function for device registration"
#create_lambda

echo "Creating IoT topic rule....."
echo "Run this step only after creating the lambda function taxidb_lambda"
read -r -p "Continue rule creation? [y/N] " response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
	lambda_arn=$(aws lambda get-function --function-name taxidb_lambda --query Configuration.FunctionArn --output text)
	cat <<EOF > rule.json
	{
          "sql": "SELECT * FROM 'iot/TAXI'", 
          "ruleDisabled": false, 
          "awsIotSqlVersion": "2016-03-23",
          "actions": [{
            "lambda": {
              "functionArn": "$lambda_arn"
            }
          }]
	}
EOF

	aws iot create-topic-rule \
		--rule-name taxi_iot_lambda_rule \
		--topic-rule-payload file://rule.json
	rm -rf rule.json
	echo "done"
else
	echo "Skipping step"
fi

