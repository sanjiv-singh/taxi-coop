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


    if [ "$db_lambda" = true ]; then
	echo "Creating taxidb_lambda"
        zip -r taxidb_lambda_package.zip taxidb_lambda.py
        aws lambda create-function \
            --function-name taxidb_lambda \
            --runtime python3.9 \
            --environment "Variables={db_user=$DB_USER,db_pass=$DB_PASSWORD,db_endpoint=$end_point,south=12.8,west=77.5,north=13.5,east=78.2}" \
            --zip-file fileb://taxidb_lambda_package.zip \
            --handler taxidb_lambda.lambda_handler \
            --role $role_arn \
            --output text \
            --vpc-config SubnetIds=$subnet_ids,SecurityGroupIds=$security_group_ids
    fi

    if [ "$query_lambda" = true ]; then
	echo "Creating taxidb_query"
        zip -r taxidb_query_package.zip taxidb_query.py
        aws lambda create-function \
            --function-name taxidb_query \
            --runtime python3.9 \
            --environment "Variables={db_user=$DB_USER,db_pass=$DB_PASSWORD,db_endpoint=$end_point,south=12.8,west=77.5,north=13.5,east=78.2}" \
            --zip-file fileb://taxidb_query_package.zip \
            --handler taxidb_query.lambda_handler \
            --role $role_arn \
            --output text \
            --vpc-config SubnetIds=$subnet_ids,SecurityGroupIds=$security_group_ids
    fi

    if [ "$register_lambda" = true ]; then
	echo "Creating taxidb_register"
	zip -r taxidb_register_package.zip taxidb_register.py
	aws lambda create-function \
	    --function-name taxidb_register \
	    --runtime python3.9 \
	    --environment "Variables={db_user=$DB_USER,db_pass=$DB_PASSWORD,db_endpoint=$end_point}" \
	    --zip-file fileb://taxidb_register_package.zip \
	    --handler taxidb_register.lambda_handler \
	    --role $role_arn \
	    --output text \
	    --vpc-config SubnetIds=$subnet_ids,SecurityGroupIds=$security_group_ids
    fi

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

if [ -z "$1" ]
  then
    echo "Creating all db related lambda functions"
    db_lambda=true
    query_lambda=true
    register_lambda=true
else
    echo "Creating $1 lambda function"
    db_lambda=false
    query_lambda=false
    register_lambda=false
    if [ "$1" == "db" ]; then
	db_lambda=true
    elif [ "$1" == "query" ]; then
	query_lambda=true
    elif [ "$1" == "register" ]; then
	register_lambda=true
    else
	echo "Invalid lambda function name"
	echo "Valid names are db, query, register"
	exit 1
    fi
fi

create_lambda db_lambda query_lambda register_lambda
sleep 5

aws lambda add-permission \
	--function-name taxidb_lambda \
	--statement-id iot-events \
	--action "lambda:InvokeFunction" \
	--principal iot.amazonaws.com

