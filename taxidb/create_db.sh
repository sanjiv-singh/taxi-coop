
STACK_NAME="taxidb"
TEMPLATE="taxidb.yml"
PARAMETERS="taxidb_params.json"

aws cloudformation create-stack \
	--stack-name $STACK_NAME \
	--template-body file://$TEMPLATE \
	--capabilities CAPABILITY_IAM \
	--parameters file://$PARAMETERS
