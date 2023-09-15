import boto3
import json
from botocore.exceptions import ClientError
iamclient = boto3.client('iam')
s3client = boto3.client('s3')



#Parse user information from inputs
def Establish_User():
    try:
        email = input('Enter email: ').strip()
        name = input('Enter full name: ')
        permissions_level = input('Enter user role permissions level: admin/guest ').strip()
        org_name = input('Enter name of organization or project user belongs to: ').strip()
        user_data = {}
        user_data['email'] = email
        user_data['name'] = name
        user_data['permissions_level'] = permissions_level
        user_data['org_name'] = org_name
        print(user_data)
    except:
        user_data = False
    return user_data



#Creates s3 bucket to store user data in a .json/ checks the existence of bucket
def Check_Bucket_List(user_data):
    users_bkt_name = 'iam-user-details-{}'.format(user_data['org_name'])
    try:
        response = s3client.head_bucket(
            Bucket = users_bkt_name
        )    
        bucket_name = users_bkt_name
        print('Users storage info bucket already created:{}'.format(users_bkt_name))
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            try:
                response1 = s3client.create_bucket(
                    Bucket = users_bkt_name
                )
                print('Created Users storage info bucket: {}'.format(users_bkt_name))
                #Uploading initial .json for iam users info
                with open ('miscellaneous_aws_automations/iam-onboarding/iam-users-info.json') as temp:
                    initial_iam_json = temp.read()
                try:
                    response2 = s3client.put_object(
                        Bucket = users_bkt_name,
                        Key = 'iam-users-info.json',
                        Body = initial_iam_json
                        )
                    bucket_name = users_bkt_name
                    print('iam users initial object stored')
                except ClientError as e:
                    print("Client error: %s" % e)
                    bucket_name = False
            except ClientError as e:
                print("Client error: %s" % e)
                bucket_name = False
    return bucket_name



#Creates IAM user and tag with some of the inputs
def Create_User(user_data):
    initial_name = user_data['name'].replace(" ", "")
    username = initial_name+'-'+user_data['permissions_level']
    print(username)
    try:
        response = iamclient.create_user(
            UserName = username,
            Tags = [
                {
                'Key': 'Access',
                'Value': user_data['permissions_level']
                },
                {
                'Key': 'AssignedProject',
                'Value': user_data['org_name']
                }            
            ]
        )
        print('Created IAM User: '+ username)
        new_iam_ids = {}
        new_iam_ids['iam_user_id'] = response['User']['UserId']
        new_iam_ids['iam_user_arn'] = response['User']['UserId']
    except ClientError as e:
        print("Client error: %s" % e)
        new_iam_ids = False
    return new_iam_ids



#Attach a managed policy conditionally to user
def Attach_Managed_Policy(user_data, new_iam_ids):
    if user_data['permissions_level'] == 'admin':
        policy_arn = 'arn:aws:iam::aws:policy/AdministratorAccess'
    elif user_data['permissions_level'] == 'guest':
        policy_arn = 'arn:aws:iam::aws:policy/ReadOnlyAccess'
    try:
        response = iamclient.attach_user_policy(
            UserName = new_iam_ids['iam_user_id'],
            PolicyArn = policy_arn
        )
        attach_policy = True
        print('atached policy to User: '+ new_iam_ids['iam_user_id'])
    except ClientError as e:
        print("Client error: %s" % e)
        attach_policy = False
    return attach_policy



#Getting IAM users object 
def Get_Users_Object(users_bucket):
    try:
        response = s3client.get_object(
           Bucket = users_bucket,
            Key = 'iam-users-info.json'
        )
        existing_users_info = json.loads(response['Body'].read().decode('utf-8'))
        print('Existing Users object info retrieved')
    except ClientError as e:
        print("Client error: %s" % e)
        existing_users_info = False
    return existing_users_info



#Updating .json to include new user information
def Update_Users_Object(user_data, bucket_name, new_iam_ids, existing_users_info):
    new_iam_user = {}
    new_iam_user['UserId'] = new_iam_ids['iam_user_id']
    new_iam_user['UserId']['Name'] = user_data['name']
    new_iam_user['UserId']['Arn'] = new_iam_ids['iam_user_arn']
    new_iam_user['UserId']['Access'] = user_data['permissions_level']
    new_iam_user['UserId']['ContactEmail'] = user_data['email']
    try:
        updated_users_info = json.dumps(existing_users_info['Users'].append(new_iam_user))
        
        response = s3client.put_object(
            Bucket = bucket_name,
            Key = 'iam-users-info.json',
            Body = updated_users_info
        )
        
        print('User {} info stored..'.format(new_iam_ids['iam_user_id']))
    except ClientError as e:
        print("Client error: %s" % e)
    return 



def main():
    b = Establish_User()
    if b != False:
        a = Check_Bucket_List(b)
        if a != False:
            c = Create_User(b)
            e = Attach_Managed_Policy(b,c)
            if c != False:
                d = Get_Users_Object(a)
                if d != False:
                    Update_Users_Object(b, a, c, d)
                else:
                    print('Function Get_user failed..')
            else:
                print('Function Create_User failed..')
        else:
            print('Function Check_Bucket failed..')
    else:
        print('Function Establish_User failed..')
if __name__ == '__main__':
    main()