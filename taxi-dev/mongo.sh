#!/bin/bash

# Check if DB_USER is set
if [ -z "$DB_USER" ]; then
  echo "DB_USER is not set"
  echo "Please set DB_USER environment variable"
  echo "e.g. export DB_USER=<username>"
  exit 1
fi

# Check if DB_PASSWORD is set
if [ -z "$DB_PASSWORD" ]; then
  echo "DB_PASSWORD is not set"
  echo "Please set DB_PASSWORD environment variable"
  echo "e.g. export DB_PASSWORD=<password>"
  exit 1
fi

# Fetch the AWS DocumentDB cluster endpoint
DB_ENDPOINT=$(aws docdb describe-db-clusters --db-cluster-identifier taxi-cluster --query 'DBClusters[0].Endpoint' --output text)

# Connect to the cluster
mongosh --tls --host $DB_ENDPOINT:27017 --sslCAFile rds-combined-ca-bundle.pem --username $DB_USER --password $DB_PASSWORD < db_setup.js

