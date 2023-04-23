#!/bin/bash


# Cleanup roles and policies
docdb_policy_arn="arn:aws:iam::aws:policy/AmazonDocDBFullAccess"

echo "Deleting IAM roles and policies"
aws iam detach-role-policy --role-name taxi-ec2-role --policy-arn $docdb_policy_arn
aws iam delete-role --role-name taxi-ec2-role

# Cleanup all ec2 instances
echo "Terminating all EC2 instances"
for id in $(aws ec2 describe-instances --query "Reservations[*].Instances[*].[InstanceId]" --output text);
do
  aws ec2 terminate-instances --instance-ids $id;
done
rm -f ip_address.txt
sleep 10

# cleanup key pair and security groups
echo "Deleting key pair"
rm -f capstone-dev.pem
aws ec2 delete-key-pair --key-name captone-dev
echo "Done"
