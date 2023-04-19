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

    aws lambda create-function \
        --function-name taxidb_lambda \
        --runtime python3.9 \
        --environment "Variables={db_user=test,db_pass=test1234,db_endpoint=mycluster.cluster-c74mo2mt0rvc.us-east-1.docdb.amazonaws.com:27017}" \
        --zip-file fileb://deployment-package.zip \
        --handler lambda_function.lambda_handler \
        --role $role_arn \
        --vpc-config SubnetIds=subnet-0a4956e09a52c594c,subnet-0aecb108377ed3b7e,subnet-0801b6c501aacb30e,subnet-0b2044c45ca0592f6,subnet-09737fb91fe99ea7e,subnet-000875ba62d350334,SecurityGroupIds=sg-0f7284c74d27fba32

}

create_lambda
