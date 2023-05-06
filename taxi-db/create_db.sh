

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
if [ -z "$DB_CLUSTER" ]; then
	DB_CLUSTER="taxi-cluster"
fi
if [ -z "$DB_INSTANCE" ]; then
	DB_INSTANCE="taxi-instance"
fi
if [ -z "$DB_INSTANCE_CLASS" ]; then
	DB_INSTANCE_CLASS="db.t3.medium"
fi


STACK_NAME="taxidb"
TEMPLATE="taxidb.yml"

aws cloudformation create-stack \
	--stack-name $STACK_NAME \
	--template-body file://$TEMPLATE \
	--capabilities CAPABILITY_IAM \
 	--parameters ParameterKey=DBClusterName,ParameterValue=$DB_CLUSTER ParameterKey=DBInstanceName,ParameterValue=$DB_INSTANCE ParameterKey=DBInstanceClass,ParameterValue=$DB_INSTANCE_CLASS ParameterKey=MasterUser,ParameterValue=$DB_USER ParameterKey=MasterPassword,ParameterValue=$DB_PASSWORD

sleep 5
