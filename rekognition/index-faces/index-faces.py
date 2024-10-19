from __future__ import print_function

import boto3
import urllib
import os

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')


# --------------- Helper Functions ------------------

def index_faces(bucket, key):

    response = rekognition.index_faces(
        Image={"S3Object":
               {"Bucket": bucket,
                "Name": key}},
        CollectionId=os.environ['COLLECTION_NAME'])
    return response


def update_index(tableName, faceId, fullName):
    dynamodb.put_item(
        TableName=tableName,
        Item={
            'RekognitionId': {'S': faceId},
            'FullName': {'S': fullName}
        }
    )

# --------------- Main handler ------------------


def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'].encode('utf8'))

    try:

        response = index_faces(bucket, key)

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            faceId = response['FaceRecords'][0]['Face']['FaceId']
            ret = s3.head_object(Bucket=bucket, Key=key)
            email = ret['Metadata']['email']
            update_index(os.environ['COLLECTION_NAME'], faceId, email)
        return response
    except Exception as e:
        print(f"Error processing object {key} from bucket {bucket}.")
        raise e