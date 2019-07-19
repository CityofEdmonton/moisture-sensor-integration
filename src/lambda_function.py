import json
from botocore.vendored import requests

print('Loading function')

client_id = 'put-your-client-id'
client_secret = 'put-your-client-id-secret'

def token_call():
    '''
    get the access token from portal api
    '''
    # api endpoint
    addr = 'https://monitor.sensoterra.com/apiportal/v2'
    url = addr + '/oauth/token'
    
    # prepare headers for http request
    content_type = 'application/json'
    headers = {'content-type': content_type}
    
    body = {
        "client_id":     client_id,
        "client_secret": client_secret,
        "grant_type":    "client_credentials",
        "scope":         "decoder"
    }
    
    # encode body using json
    body = json.dumps(body)
    
    # send http request with image and receive response
    response = requests.post(
    url, data=body, headers=headers)
    return response.json()["access_token"]
    
    
def decode_call(DevEUI,port,payload,count):
    # api endpoint
    addr = 'https://monitor.sensoterra.com/apiportal/v2'
    url = addr + '/decoder/%s/payload'%(DevEUI)

    # get the token for authorization
    token = token_call()

    # prepare headers for http request
    content_type = 'application/json'
    headers = {'content-type': content_type,
        "Authorization": "Bearer %s"%(token)
    }

    # build a body dict to send to server
    body = {"port": port,
            "payload": payload,
            "count": count}
    print(body)
    # encode body using json
    body = json.dumps(body)


    # send http request with image and receive response
    response = requests.post(
        url, data=body, headers=headers)
    return response.json()


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    operations = {
        'POST': lambda DevEUI,port,payload,count : decode_call(DevEUI,port,payload,count),
    }

    operation = event['httpMethod']
    if operation in operations:
        print(event['body'])
        body = json.loads(event['body'])
        print(body)
        payload = body['DevEUI_uplink']['payload_hex']
        DevEUI = body['DevEUI_uplink']['DevEUI']
        port = body['DevEUI_uplink']['FPort']
        count = body['DevEUI_uplink']['FCntUp']
        
        response = respond(None, operations[operation](DevEUI,port,payload,count))
        print(response)
        return response
    else:
        response = respond(ValueError('Unsupported method "{}"'.format(operation)))
        print(response)
        return response
