#!/bin/bash

aws lambda delete-function --function-name taxidb_register
aws lambda delete-function --function-name taxidb_lambda
aws cloudformation delete-stack --stack-name taxidb

