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

attribute_name = 'iot:Connection.Thing.ThingTypeName'
iot_certificate_policy_document = json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iot:Connect",
                "iot:Publish",
                "iot:Subscribe",
                "iot:Receive",
                "iot:AssumeRoleWithCertificate"
            ],
            "Resource": "*"
        }
    ]
})

iot_policy_doc = {
    "Version":"2012-10-17",
    "Statement":[
      {
        "Effect":"Allow",
        "Action":[
          "iot:Connect"
        ],
        "Resource":[
          "*"
        ]
      },
      {
        "Effect":"Allow",
        "Action":[
          "iot:Publish",
          "iot:Subscribe",
          "iot:Receive"
        ],
        "Resource":[
          "*"
        ],
      }
    ]
}

iot_registration_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration'
iot_logging_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTLogging'
iot_rule_actions_policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSIoTRuleActions'
docdb_policy_arn = 'arn:aws:iam::aws:policy/AmazonDocDBFullAccess'


def load_config(file):
    with open(file) as f:
        config = json.loads(f.read())
    return config


def create_policy(client, policy):
    try:
        resp = client.create_policy(
            policyName=policy,
            policyDocument=json.dumps(iot_policy_doc)
        )
    except Exception:
        print(f'Policy {policy} already exists. Skipping.')


def create_certificate(client, thing_name, cert_path, policy):
    resp = client.create_keys_and_certificate(setAsActive=True)
    data = json.loads(json.dumps(resp, sort_keys=False, indent=4))
    for element in data:
        if element == 'certificateArn':
            cert_arn = data['certificateArn']
        if element == 'keyPair':
            key_pair = data['keyPair']
    with open(f'{cert_path}/{thing_name}_public.key', 'w+') as pubkey_file:
        pubkey_file.write(key_pair['PublicKey'])
    with open(f'{cert_path}/{thing_name}_private.key', 'w+') as prikey_file:
        prikey_file.write(key_pair['PrivateKey'])
    with open(f'{cert_path}/{thing_name}_device.pem', 'w+') as cert_file:
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
    resp = client.create_thing(
        thingName=device,
        thingTypeName=config.get("thing_type")
    )
    resp = client.add_thing_to_thing_group(
        thingName=device,
        thingGroupName=config.get("thing_group")
    )
    create_certificate(client, device, cert_path, policy)


def create_role(client, iam_role_name):
    resp = client.create_role(
        RoleName=iam_role_name,
        AssumeRolePolicyDocument=assume_role_policy_document
    )
    role = resp.get('Role')
    resp = client.attach_role_policy(
        RoleName=iam_role_name, PolicyArn=iot_registration_policy_arn)
    resp = client.attach_role_policy(
        RoleName=iam_role_name, PolicyArn=iot_logging_policy_arn)
    resp = client.attach_role_policy(
        RoleName=iam_role_name, PolicyArn=iot_rule_actions_policy_arn)
    resp = client.attach_role_policy(
        RoleName=iam_role_name, PolicyArn=docdb_policy_arn)
    return role.get('Arn')



if __name__ == '__main__':
    config = load_config("config.json")

    iot_client = boto3.client('iot')
    iam_client = boto3.client('iam')

    cert_path = config.get("cert_path")
    policy = config.get("policy_name")
    create_policy(iot_client, policy)

    props = {'thingTypeDescription': config.get("thing_type_desc")}
    try:
        type_resp = iot_client.create_thing_type(
            thingTypeName=config.get("thing_type"),
            thingTypeProperties=props
        )
    except Exception:
        print(f'ThingType {config.get("thing_type")} already exists. Skipping.')

    props = {'thingGroupDescription': config.get("thing_group_desc")}
    try:
        group_resp = iot_client.create_thing_group(
            thingGroupName=config.get("thing_group"),
            thingGroupProperties=props
        )
    except Exception:
        print(f'ThingGroup {config.get("thing_group")} already exists. Skipping.')


    print("Creating IoT devices for Taxies ")
    for i in range(10):
        create_thing(iot_client, f'TAXI_{i}', cert_path, policy)

    # delete_role(iam_client, config.get("role"))
    print("Creating role ", config.get("role"))
    role_arn = create_role(iam_client, config.get("role"))
    time.sleep(30)
    # delete_rule(iot_client, config.get("rule"))
    # print("Creating message routing rule ", config.get("rule"))
    # create_rule(iot_client, role_arn, config.get("rule"))
