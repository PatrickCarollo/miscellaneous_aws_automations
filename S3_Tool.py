#Uploads/deletes input-selected local file to an s3 bucket as an object...
import boto3
import json
from botocore.exceptions import ClientError 
import io
from zipfile import ZipFile, ZIP_DEFLATED
s3client = boto3.client('s3')



#Aquire bucket names in aws account
def List_Buckets():
    try:
        response = s3client.list_buckets()
        LFbuckets = response['Buckets']
        for x in LFbuckets:
            print(x['Name'])
        bucketdata = input(' ^ Choose bucket ^ : ') 
        return bucketdata
    except ClientError as e:
        print("Client error: %s" % e)


#List bucket options for file to be uplaoded and proceed to upload
def S3_Uploader(bucket_name):
    pathdata = input('Enter local file path: ')
    usercomm = input('Rename key?: y/n: ')
    if usercomm == 'n':
        indexed = pathdata.rfind('/')
        if indexed != -1:
            key = pathdata[indexed+1:]
        else: 
            key = pathdata
    elif usercomm == 'y':
        key = input('Desired file name: ')
    else:
        print('invalid comm')
    if '.py' or '.js' in key:
        inputs = input('zip this code object?: y/n  ')
        if inputs == 'y':
            object0 = io.BytesIO()
            with ZipFile(object0,'w',ZIP_DEFLATED) as obj:
                obj.write(pathdata, arcname = key)
            object0.seek(0)
            integ = key.find('.py')
            keydata = key[:integ] + '.zip'
        else:
            with open(pathdata) as obj:
                object0 = obj.read()
                keydata = key
    else:
        with open(pathdata) as obj:
            object0 = obj.read()
            keydata = key
    try:
        response = s3client.put_object(
            Bucket = bucket_name ,
            Body = object0 ,
            Key = keydata
        )
        #Success confirmation
        if 'ResponseMetadata' in response:
            rid = response['ResponseMetadata']['RequestId']
            print('File Uploaded successfully: ' + keydata + '    RequestID: '+ rid)
    #Api fail
    except ClientError as e:
        print("Client error: %s" % e)


def S3_List_Object(bucket_name):
    try:
        response = s3client.list_objects(
            Bucket = bucket_name
        )
        object_keys = []
        if 'Contents' in response:
            print('objects found: ')
            for x in response['Contents']:
                object_keys.append(x['Key'])
                print(x['Key'])
        else:
            print('no objects found for deletion')
        return object_keys
    except ClientError as e:
        print("Client error: %s" % e)


def S3_Objects_Delete(bucket_name, object_keys):    
    if input('empty bucket: continue? y/n: ') == 'y':
        object_array = []
        for x in object_keys:
            dict_obj = {}
            dict_obj['Key'] = x
            object_array.append(dict_obj)
        
        try:
            response = s3client.delete_objects(
                Bucket = bucket_name,
                Delete = {'Objects': object_array}
            )
            if 'Deleted' in response:
                print('objects deleted')
                data = 200
                
            else:
                data = 0
                print('objects failed to delete')
            return data
        except ClientError as e:
            print("Client error: %s" % e)
    else:
        print('stopped')


def S3_Bucket_Delete(bucket_name, empty_status):
    if input('proceed to delete bucket? y/n: ') == 'y':
        try:
            response = s3client.delete_bucket(
                Bucket = bucket_name,
        
            )
            print(response)
        except ClientError as e:
            print("Client error: %s" % e)
    else:
        print('stopped')



def main():
    z = List_Buckets()
    if z == 0:
        print('No buckets found in account')
    else:
        command0 = input('upload/delete: ')
        if command0 =='upload':
            S3_Uploader(z)
        elif command0 == 'delete':
            x = S3_List_Object(z)
            y = S3_Objects_Delete(z, x)
            S3_Bucket_Delete(z, y)

if __name__ =='__main__':
    main()