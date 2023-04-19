create_lambda () {
    lambda_execution_policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    docdb_policy_arn="arn:aws:iam::aws:policy/AmazonDocDBFullAccess"
    aws iam create-role --role-name taxidb-lambda-role \
        --assume-role-policy-document file://lambda_policy.json --output text
    aws iam attach-role-policy --role-name taxidb-lambda-role \
        --policy-arn $lambda_execution_policy_arn
    aws iam attach-role-policy --role-name taxidb-lambda-role \
        --policy-arn $docdb_policy_arn
    aws iam put-role-policy \
	    --role-name taxidb-lambda-role \
	    --policy-name taxi-lambda-ec2 \
	    --policy-document file://lambda_ec2_policy.json
    role_arn=$(aws iam get-role --role-name "taxidb-lambda-role" \
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


    zip -r taxidb_lambda_package.zip taxidb_lambda.py
    aws lambda create-function \
        --function-name taxidb_lambda \
        --runtime python3.9 \
        --environment "Variables={db_user=$DB_USER,db_pass=$DB_PASSWORD,db_endpoint=$end_point}" \
        --zip-file fileb://taxidb_lambda_package.zip \
        --handler taxidb_lambda.lambda_handler \
        --role $role_arn \
        --vpc-config SubnetIds=$subnet_ids,SecurityGroupIds=$security_group_ids

}

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

create_lambda
sleep 5

aws lambda add-permission \
	--function-name taxidb_lambda \
	--statement-id iot-events \
	--action "lambda:InvokeFunction" \
	--principal iot.amazonaws.com

