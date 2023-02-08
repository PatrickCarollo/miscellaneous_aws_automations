import boto3
import json
from botocore.exceptions import ClientError
cfclient = boto3.client('cloudformation')
iamclient = boto3.client('iam')


def Temp_Ec2_Dev_Env():
    key_name = input('keypair name: ')
    with open('AWS-MS-Infrastructure/Development/template.yml') as obj:
        temlate_body = obj.read()
    role = Get_RoleARN()
    if role != 0:
        try:
            response = cfclient.create_stack(
                StackName = 'Dev_Environment',
                TemplateBody = temlate_body,
                Capabilities = 'CAPABILITY_NAMED_IAM',
                Parameters = [
                    {
                        'ParameterKey': 'accesscreds',
                        'ParameterValue': 'string',
                    } 
                ],
                RoleARN = role
            )
            if 'StackId' in response:
                print('stack launch initiated')
            else:
                print('stack launch fail')
        except ClientError as e:
            print("Client error: %s" % e)
    


def Get_RoleARN():
    try:
        response = iamclient.get_role(
            RoleName = 'MainMSStackServiceRole'
        )
        if 'Arn' in response['Role']:
            data = response['Role']['Arn'].strip()
            print(data)
        else:
            data = 0
            print('Error getting role for stack creation')
        return data
    except ClientError as e:
        print("Client error: %s" % e)
        


def main():
    Temp_Ec2_Dev_Env()

if __name__ == '__main__':
    main()