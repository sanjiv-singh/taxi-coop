import boto3
import json
import time

assume_role_policy_document = json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Principal": {
            "Service": "iot.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
        }
    ]
})

iot_registration_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration'
iot_logging_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTLogging'
iot_role_actions_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions'
dynamodb_policy_arn = 'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'

def load_config(file):
    with open(file) as f:
        config = json.loads(f.read())
    return config

def create_certificate(client, thing_name, cert_path, policy):
    resp = client.create_keys_and_certificate(setAsActive=True)
    data = json.loads(json.dumps(resp, sort_keys=False, indent=4))
    for element in data:
        if element == 'certificateArn':
            cert_arn = data['certificateArn']
        if element == 'keyPair':
            key_pair = data['keyPair']
    with open(f'{cert_path}/{thing_name}_public.key', 'w') as pubkey_file:
        pubkey_file.write(key_pair['PublicKey'])
    with open(f'{cert_path}/{thing_name}_private.key', 'w') as prikey_file:
        prikey_file.write(key_pair['PrivateKey'])
    with open(f'{cert_path}/{thing_name}_device.pem', 'w') as cert_file:
        cert_file.write(data['certificatePem'])

    resp = client.attach_policy(
		    policyName=policy,
		    target=cert_arn
    )
    resp = client.attach_thing_principal(
		    thingName=thing_name,
		    principal=cert_arn
    )

def create_thing(client, device, cert_path, policy):
    props = {'thingTypeDescription': device.get("thing_type_desc")}
    type_resp = client.create_thing_type(
		    thingTypeName=device.get("thing_type"),
		    thingTypeProperties=props
    )
    props = {'thingGroupDescription': device.get("thing_group_desc")}
    group_resp = client.create_thing_group(
		    thingGroupName=device.get("thing_group"),
		    thingGroupProperties=props
    )
    resp = client.create_thing(
                thingName=device.get("device_id"),
                thingTypeName=device.get("thing_type")
    )
    resp = client.add_thing_to_thing_group(
                thingName=device.get("device_id"),
                thingGroupName=device.get("thing_group")
    )
    create_certificate(client, device.get("device_id"), cert_path, policy)

def create_table(dynamodb, table_name):
    table = dynamodb.create_table(
	TableName=table_name,
	KeySchema=[
        {
            'AttributeName': 'deviceid',
            'KeyType': 'HASH'  #Partition key
        },
        {
            'AttributeName': 'timestamp',
            'KeyType': 'RANGE'  #Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'deviceid',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'timestamp',
            'AttributeType': 'S'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    })
    table.wait_until_exists()

def delete_role(client, iam_role_name):
    client.detach_role_policy(
        RoleName=iam_role_name,
        PolicyArn=iot_registration_policy_arn
    )
    client.detach_role_policy(
        RoleName=iam_role_name,
        PolicyArn=iot_logging_policy_arn
    )
    client.detach_role_policy(
        RoleName=iam_role_name,
        PolicyArn=iot_role_actions_policy_arn
    )
    client.detach_role_policy(
        RoleName=iam_role_name,
        PolicyArn=dynamodb_policy_arn
    )
    client.delete_role(RoleName=iam_role_name)

def create_role(client, iam_role_name):
    resp = client.create_role(
        RoleName=iam_role_name,
        AssumeRolePolicyDocument=assume_role_policy_document
    )
    role = resp.get('Role')
    resp = client.attach_role_policy(RoleName=iam_role_name, PolicyArn=iot_registration_policy_arn)
    resp = client.attach_role_policy(RoleName=iam_role_name, PolicyArn=iot_logging_policy_arn)
    resp = client.attach_role_policy(RoleName=iam_role_name, PolicyArn=iot_role_actions_policy_arn)
    resp = client.attach_role_policy(RoleName=iam_role_name, PolicyArn=dynamodb_policy_arn)
    return role.get('Arn')

def delete_rule(client, rule_name):
    resp = client.delete_topic_rule(ruleName=rule_name)

def create_rule(client, role_arn, rule_name):
    response = client.create_topic_rule(
        ruleName=rule_name,
        topicRulePayload={
            'sql': 'SELECT * FROM "iot/bsm"',
            'description': 'Rule to ingest device data to DynamoDB',
            'actions': [
                {
                    'dynamoDBv2': {
                        'roleArn': role_arn,
                        'putItem': {
                            'tableName': 'bsm_data'
                        }
                    }
                }
            ]
        }
    )



if __name__ == '__main__':
    config = load_config("config.json")

    iot_client = boto3.client('iot')
    dynamodb = boto3.resource('dynamodb')
    iam_client = boto3.client('iam')

    cert_path = config.get("cert_path")
    policy = config.get("policy_name")

    print("Creating devices ", ' '.join([d.get("device_id") for d in config.get("devices")]))
    for device in config.get("devices"):
        create_thing(iot_client, device, cert_path, policy)
    
    print("Creating table ", config.get("raw_table"))
    create_table(dynamodb, config.get("raw_table"))
    print("Creating table ", config.get("agg_table"))
    create_table(dynamodb, config.get("agg_table"))
    print("Creating table ", config.get("alerts_table"))
    create_table(dynamodb, config.get("alerts_table"))

    #delete_role(iam_client, config.get("role"))
    print("Creating role ", config.get("role"))
    role_arn = create_role(iam_client, config.get("role"))
    time.sleep(30)
    #delete_rule(iot_client, config.get("rule"))
    print("Creating message routing rule ", config.get("rule"))
    create_rule(iot_client, role_arn, config.get("rule"))
