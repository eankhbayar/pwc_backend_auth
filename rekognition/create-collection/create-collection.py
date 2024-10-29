import boto3
import os
import json
import logging
import requests

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

client = boto3.client('rekognition')


def handler(event, context):
    responseStatus = 'SUCCESS'
    responseData = {'Message': ''}

    collectionId = os.environ['COLLECTION_NAME']

    LOGGER.info('CollectionId: ' + collectionId)

    sendResponse(event, context, responseStatus, responseData)

    if event['RequestType'] == 'Create':
        response = client.create_collection(CollectionId=collectionId)
        responseData = {'Message': response['CollectionArn']}
        sendResponse(event, context, responseStatus, responseData)
    if event['RequestType'] == 'Delete':
        response = client.delete_collection(CollectionId=collectionId)
        sendResponse(event, context, responseStatus, responseData)
    return


def sendResponse(event, context, responseStatus, responseData):
    responseBody = {'Status': responseStatus,
                    'Reason': 'See the details in CloudWatch Log Stream: ' + context.log_stream_name,
                    'PhysicalResourceId': context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId'],
                    'Data': responseData}
    LOGGER.info('RESPONSE BODY:\n' + json.dumps(responseBody))
    try:
        req = requests.put(event['ResponseURL'], data=json.dumps(responseBody))
        if req.status_code != 200:
            LOGGER.info(req.text)
            raise Exception('Failed to send response to CFN')
        return
    except requests.exceptions.RequestException as e:
        LOGGER.info(e)
        raise


if __name__ == '__main__':
    handler('event', 'handler')
