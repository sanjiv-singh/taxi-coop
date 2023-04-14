import boto3
import json


default_thing_type = 'TAXI'

iot_client = boto3.client('iot')

def load_config(file):
    with open(file) as f:
        config = json.loads(f.read())
    return config


def delete_things():

    resp = iot_client.list_things(thingTypeName=default_thing_type)
    thing_names = [thing.get('thingName') for thing in resp.get('things')]
    
    for thing in thing_names:
        try:
            principals = iot_client.list_thing_principals(thingName=thing)
        except Exception as e:
            print(f"ERROR listing thing principals: {e}")
            principals = {'principals': []}

        for arn in principals['principals']:
            cert_id = arn.split('/')[1]
            print(f"  arn: {arn} cert_id: {cert_id}")

            detach_thing = iot_client.detach_thing_principal(thingName=thing, principal=arn)
            print(f"  DETACH THING: {detach_thing}")

            upd_cert = iot_client.update_certificate(certificateId=cert_id,newStatus='INACTIVE')
            print(f"  INACTIVE: {upd_cert}")

            policies = iot_client.list_principal_policies(principal=arn)

            for pol in policies['policies']:
                pol_name = pol['policyName']
                print(f"    pol_name: {pol_name}")
                detach_pol = iot_client.detach_policy(policyName=pol_name,target=arn)
                print(f"    DETACH POL: {detach_pol}")

            del_cert = iot_client.delete_certificate(certificateId=cert_id,forceDelete=True)
            print(f"  DEL CERT: {del_cert}")
            del_thing = iot_client.delete_thing(thingName=thing)
    # dep = iot_client.deprecate_thing_type(thingTypeName=default_thing_type)
    # del_thing_type = iot_client.delete_thing_type(thingTypeName=default_thing_type)


if __name__ == '__main__':

    config = load_config("config.json")
    ans = input(f'Delete all things (y/n)') or "n"
    if ans in ('y', 'Y'):
        # Delete Things
        delete_things()

        # Delete Thing Group
        resp = iot_client.delete_thing_group(thingGroupName=config.get("devices")[0]["thing_group"])
        # Delete IoT Policy
        resp = iot_client.delete_policy(policyName=config.get("policy_name"))
    

