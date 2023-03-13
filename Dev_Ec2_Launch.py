import boto3
import json
from botocore.exceptions import ClientError
cfclient = boto3.client('cloudformation')
iamclient = boto3.client('iam')


def Temp_Ec2_Dev_Env():
    with open('Miscellaneous_AWS_Automations/Dev_Ec2_Launch.yml') as obj:
        temlate_body = obj.read()
    role = Get_RoleARN()
    key_pairname = input('enter name of keypair for ssh access allow: ')
    if role != 0:
        try:
            response = cfclient.create_stack(
                StackName = 'Dev-Environment-Stack',
                TemplateBody = temlate_body,
                Capabilities = ['CAPABILITY_NAMED_IAM'],
                Parameters = [
                    {
                        'ParameterKey': 'accesscreds',
                        'ParameterValue': key_pairname,
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
            RoleName = 'MySampleStackServiceRole'
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