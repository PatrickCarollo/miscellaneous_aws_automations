import boto3
import json
import time
ambclient = boto3.client('managedblockchain')
ssmclient = boto3.client('ssm')


command = input('create/delete/list: ').strip()
    

def Create_Managed_Blockchain_Node():    
    response = ambclient.create_node(
        NetworkId = 'n-ethereum-goerli',
        NodeConfiguration = {
            'InstanceType': 'bc.t3.large',
            'AvailabilityZone': 'us-east-1a',
        }
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        data = response['NodeId'].strip()
        print('Created Eth node successfully: ' + data)
    else:
        data = False
        print('Failed to create Eth node')
    return data


def Update_NodeId_Store(node_id):
    response = ssmclient.put_parameter(
        Overwrite = True,
        Name = 'EthNodeId-A',
        Value = node_id,
        Type  = 'String'
    )
    if 'Version' in response:
        print('Node id for Eth updated in Parameter Store: ' + node_id)
    else:
        print('Node id for Eth failed to upload to Parameter Store..')
  

def Delete_Managed_Blockchain_Node(node_id_for_deletion):
    response = ambclient.delete_node(
        NetworkId = 'n-ethereum-goerli',
        NodeId = node_id_for_deletion
    )
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('Eth node deleted successfully:  ' + node_id_for_deletion)
    else:
        print('Eth node failed to delete')


def Get_Parameter():
    response = ssmclient.get_parameter(
        Name = 'EthNodeId-A'
    )
    if 'Value' in response['Parameter']:
        data = response['Parameter']['Value']
        print('Fetched nodeid parameter EthNodeId-A')
    else:
        data = False
        print('Failed to get node id from parameter store..')
    return data


def Check_For_Node_Status(node_id):
    while True:
        response = ambclient.get_node(
            NetworkId = 'n-ethereum-goerli',
            NodeId = node_id
        )
        if response['Node']['Status'] == 'CREATING' or response['Node']['Status'] == 'UPDATING':
            print('Node status found as CREATING/UPDATING: '+ node_id +'.. cannot delete')
            time.sleep(45)
        else:
            print('Node status found to be available for deletion..deleting:  ' + node_id )
            break
            
        
def List_Recent_Managed_Blockchain_Nodes():
    response = ambclient.list_nodes(
        NetworkId = 'n-ethereum-goerli',
        MaxResults = 5
    )
    print(response['Nodes'])


def main():
    if command == 'create':
        a = Create_Managed_Blockchain_Node()   
        if a != False:
            Update_NodeId_Store(a)
    elif command == 'delete':
        b = Get_Parameter()
        Check_For_Node_Status(b)
        Delete_Managed_Blockchain_Node(b)
    elif command == 'list':
        List_Recent_Managed_Blockchain_Nodes()
    else:
        print('bad command')
if __name__ =='__main__':
    main()