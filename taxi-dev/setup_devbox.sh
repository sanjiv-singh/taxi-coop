#!/bin/bash

AMI=ami-007855ac798b5175e

create_key_pair () {
    # create a fresh key pair
    if [ -f capstone-dev.pem ]; then
	echo "Deleting existing key pair capstone-dev"
	chmod 600 capstone-dev.pem
	rm -f capstone-dev.pem
    fi
    aws ec2 create-key-pair --key-name capstone-dev --query 'KeyMaterial' | sed -e 's/"//g' -e 's/\\n/\n/g' > capstone-dev.pem
    chmod 400 capstone-dev.pem
}

my_ip=$(curl https://checkip.amazonaws.com)


create_ec2_instance () {
    # Create a new ec2 instance
    db_sg=$(aws ec2 describe-security-groups --query 'SecurityGroups[*].GroupId' --output text)
    echo "Will be using security group $db_sg"
    db_subnets=$(aws ec2 describe-subnets --query 'Subnets[*].SubnetId' --output text)
    for subnet in $db_subnets; do
	subnet_az=$(aws ec2 describe-subnets --subnet-id $subnet --query 'Subnets[*].AvailabilityZone' --output text)
	if [ $subnet_az == "us-east-1a" ]; then
	    db_subnet=$subnet
	fi
    done
    echo "Will be using subnet $db_subnet in availability zone us-east-1a"
    instance_id=$(aws ec2 run-instances --image-id $AMI --instance-type t2.micro --key-name capstone-dev --subnet-id $db_subnet --query 'Instances[*].[InstanceId]' --output text)
    aws ec2 authorize-security-group-ingress --group-id $db_sg --protocol tcp --port 22 --cidr 0.0.0.0/0
}

prepare_instance () {
    # Grant IAM role to access Document DB
    docdb_policy_arn="arn:aws:iam::aws:policy/AmazonDocDBFullAccess"
    aws iam create-role --role-name taxi-ec2-role --assume-role-policy-document file://ec2_policy.json --output text
    aws iam attach-role-policy --role-name taxi-ec2-role --policy-arn $docdb_policy_arn

    # Obtain the public IP addr of the new instance
    ip_address=$(aws ec2 describe-instances --filter "Name=instance-id,Values=$instance_id" --query 'Reservations[*].Instances[*].[PublicIpAddress]' --output text)
    echo $ip_address > ip_address.txt
    sleep 5
    # Prepare the instance
    ssh -i capstone-dev.pem -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@$ip_address "echo Login successful"
    scp -i capstone-dev.pem -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null prepare.sh mongo.sh db_setup.js rds-combined-ca-bundle.pem ubuntu@$ip_address:.
    ssh -i capstone-dev.pem -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null ubuntu@$ip_address "./prepare.sh"
}

echo "Creating key pair capstone-dev"
create_key_pair
sleep 5
echo "Creating ec2 instance"
create_ec2_instance
echo "Waiting for instance to be ready"
sleep 30
echo "Preparing ec2 instance"
prepare_instance
echo "Done"

echo "Do you want to enable ssh port forwarding from localhost:27017 to AWSDocDB Cluster? (y/n)"
read answer
if [ $answer == "y" ]; then
    ssh -i capstone-dev.pem -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null -f -L 27017:$primary_endpoint:27017 ubuntu@$ip_address -N
    echo "Now you can connect to the AWSDocDB Cluster using localhost:27017"
    echo "e.g. mongo --tls --tlsAllowInvalidHostnames --tlsCAFile rds-combined-ca-bundle.pem --host localhost:27017 --username <DB_USER> --password <DB_PASSWORD>"
    echo "Load and execute the file db_setup.js to create the database, collections and the required indices"
else
    echo "Now login to the instance, set DB_USER and DB_PASSWORD environment variables"
    echo "and run ./mongo.sh"
    echo "e.g. ssh -i capstone-dev.pem ubuntu@$ip_address"
    echo "./mongo.sh"
fi

