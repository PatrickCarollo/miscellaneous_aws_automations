import boto3
from botocore.exceptions import ClientError
from zipfile import ZipFile, ZIP_DEFLATED


cfclient = boto3.client('cloudformation')
iamclient = boto3.client('iam')


def Create_Ms_Stack():
    with open('Miscellaneous_AWS_Automations/Micro-Service_Config.yml') as body:
        template_body = body
    stack_name = input('Create name for ms stack: ')
    projectid = 'MySampleStack'
    try:
        response = cfclient.create_stack(
            StackName = stack_name,
            Capabilities = ['CAPABILITY_NAMED_IAM'],
            TemplateBody = template_body,
            RoleARN = Get_RoleARN,
            Parameters = [
                {
                    'ParameterKey': 'projectid',
                    'ParameterValue': projectid
                }
            ]
        )
        if 'StackId' in response:
            print('create_stack successful')
        else:
            print('create_stack failed')
    except ClientError as e:
        print("Client error: %s" % e)
        


def Get_RoleARN():
    try:
        response = iamclient.get_role(
            RoleName = 'MySampleStacksRole'
        )
        if 'Arn' in response['Role']:
            data = response['Role']['Arn'].strip()
            print('fetched role arn: ' + data)
        else:
            data = 0
            print('error getting role for stack creation')
        return data
    except ClientError as e:
        print("Client error: %s" % e)
        


def main():        
    Create_Ms_Stack()
if __name__ == '__main__':
    main()