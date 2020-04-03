import json
import os
import ast
import uuid
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import time

client = boto3.client(
    'ses'
)


def handler_name(event, context):
    # print("hi")
    message = event['Records'][0]['Sns']['Message']
    # message = event['key1']
    print("From SNS: " + message)
    print(type(message))
    json_dict = json.loads(message)
    print(json_dict['email_id']['StringValue'])
    email_id = json_dict['email_id']['StringValue']

    domain = os.environ['domain']

    sender = "no-reply@" + domain
    print(sender)

    to = sender

    str_bills = json_dict['bills_list']['StringValue']

    bills = ast.literal_eval(str_bills)

    print(str_bills)
    print(type(str_bills))

    # print(bills[0])
    id = bills[0]
    id = uuid.UUID(id)
    print(id)
    print(type(id))

    email_body = ""
    for i in range(0, len(bills)):
        print(i)

        email_body += "<p><a href='#'>http://" + domain + "/v1/bill/" + bills[i] + "</a></p><br>"

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('csye6225')
    str = "value of dyanmo is {value}".format(value=dynamodb)
    print(str)
    print(table)
    seconds = 60*60
    ttl = int(time.time()) + seconds
    try:
        response = table.get_item(
            Key={
                'email': email_id
            })
        print(response)
        if 'Item' not in response:
            print("inside put operation")
            response = table.put_item(
                Item={
                    'email': email_id,
                    'TTL': ttl
                })

            print("response is {val}".format(val=response))
            # print(response['Item'])

            response = client.send_email(
                Destination={
                    'ToAddresses': [to],
                },
                Message={
                    'Body': {
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': email_body,
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': 'List of your due bills',
                    },
                },
                Source=sender,
            )

    except ClientError as e:
        print(e.response['Error']['Message'])
    return message

