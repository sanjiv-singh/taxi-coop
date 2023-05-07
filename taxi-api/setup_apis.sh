#!/bin/bash

# This script will build the Lambda Functions for the various APIs.

# Check is DB_USER and DB_PASSWORD are set
if [ -z "$DB_USER" ]; then
    echo "DB_USER is not set"
    echo "Please set the DB_USER environment variable"
    echo "export DB_USER=<your db user>"
    exit 1
fi
if [ -z "$DB_PASSWORD" ]; then
    echo "DB_PASSWORD is not set"
    echo "Please set the DB_PASSWORD environment variable"
    echo "export DB_PASSWORD=<your db password>"
    exit 1
fi


# Build the lambda functions
sam build

# Copy the RDS CA bundle to the build directory of function that needs to call DocumentDB
cp ../taxi-db/package/rds-combined-ca-bundle.pem .aws-sam/build/TCTaxisFunction/
cp ../taxi-db/package/rds-combined-ca-bundle.pem .aws-sam/build/TCRequestRideFunction/
cp ../taxi-db/package/rds-combined-ca-bundle.pem .aws-sam/build/TCUserFunction/
cp ../taxi-db/package/rds-combined-ca-bundle.pem .aws-sam/build/TCBookRideFunction/

# Query AWS to get the required parameters for deployment

# Get the dbcluster endpoint
DB_ENDPOINT=$(aws rds describe-db-clusters --db-cluster-identifier taxi-cluster --query "DBClusters[0].Endpoint" --output text)
# Set DB USER and PASSWORD
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD

# Get the VPC Security Group IDs
VPC_SECURITY_GROUP_IDS=$(aws rds describe-db-clusters --db-cluster-identifier taxi-cluster --query "DBClusters[0].VpcSecurityGroups[*].VpcSecurityGroupId" --output text)

# Get the VPC Subnet IDs
VPC_SUBNET_IDS=""
for subnet in $(aws ec2 describe-subnets --query Subnets[].SubnetId --output text); do
    if [ -z "$VPC_SUBNET_IDS" ]; then
        VPC_SUBNET_IDS+=$subnet
    else
        VPC_SUBNET_IDS+=","
        VPC_SUBNET_IDS+=$subnet
    fi
done

# Get Register Lambda Arn
REGISTER_LAMBDA_ARN=$(aws lambda get-function --function-name taxidb_register --query Configuration.FunctionArn --output text)

# Deploy the lambda functions using sam deploy
sam deploy --stack-name taxi-coop --parameter-overrides SouthWest=12.8,77.5 NorthEast=13.5,78.2 DBUser=$DB_USER DBPassword=$DB_PASSWORD DBEndPoint=$DB_ENDPOINT DBSecurityGroups=$VPC_SECURITY_GROUP_IDS DBSubnets=$VPC_SUBNET_IDS RegisterLambdaArn=$REGISTER_LAMBDA_ARN


echo "Done"

echo "You may cleanup the deployment by running the command"
echo "sam delete --stack-name taxi-coop"

