import json
import os
import datetime
import boto3
from newsapi import NewsApiClient
from config import ALL_SOURCES, USER_PREFERENCES


def lambda_handler_get_news_from_news_api(event, context):
    newsapi = NewsApiClient(api_key=os.getenv('NEWSAPI_ACCESS_KEY'))
    all_articles = list()
    time_now = datetime.datetime.now()
    one_min_before = time_now - datetime.timedelta(days=1, minutes=1)
    sqs_message_dict = dict()
    for i in USER_PREFERENCES:
        response = newsapi.get_everything(q=i.lower(),
                                          sources=','.join(ALL_SOURCES),
                                          from_param=one_min_before.strftime('%Y-%m-%dT%H:%M:%S'),
                                          to=time_now.strftime('%Y-%m-%dT%H:%M:%S'),
                                          language='en',
                                          sort_by='relevancy',
                                          page=1)
        if response['status'] == 'ok':
            if response['totalResults'] > 0:
                for i in response['articles']:
                    sqs_message_dict[i['title']] = i['description']
    # Send message to SQS queue
    sqs = boto3.client('sqs')
    sqs_message_dict['useremail'] = 'abc@gmail.com'
    queue_url = os.getenv('QUEUE_URL')
    sqs_response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=0,
        MessageBody=json.dumps(sqs_message_dict)
    )
    return {
        "statusCode": 200,
        "body": json.dumps({
            "response": sqs_response,
        }),
    }
