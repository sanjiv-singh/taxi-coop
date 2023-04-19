# Description: Update a lambda function with a zip file
# Usage: update_lambda.sh <function_name> <zip_file>

DEFAULT_FUNCTION_NAME="taxidb_lambda"
DEFAULT_ZIP_FILE="taxidb_lambda_package.zip"

if [ -z "$1" ]; then
    echo "No function name provided, using default: $DEFAULT_FUNCTION_NAME"
    FUNCTION_NAME=$DEFAULT_FUNCTION_NAME
else
    FUNCTION_NAME=$1
fi

if [ -z "$2" ]; then
    echo "No zip file provided, using default: $DEFAULT_ZIP_FILE"
    ZIP_FILE=$DEFAULT_ZIP_FILE
else
    ZIP_FILE=$2
fi


aws lambda update-function-code --function-name $FUNCTION_NAME --zip-file fileb://$ZIP_FILE
