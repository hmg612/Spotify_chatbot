import sys
import os
import boto3

from boto3.dynamodb.conditions import Key, Attr

def main():

    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2',
        endpoint_url='http://dynamodb.ap-northeast-2.amazonaws.com')
    except:
        logging.error('could not connect to dynamodb')
        sys.exit(1)

    table = dynamodb.Table('top_tracks')

    # response = table.get_item(
    #     Key={
    #         'artist_id': '00FQb4jTyendYWaN8pK0wa',
    #         'id': '0Oqc0kKFsQ6MhFOLBNZIGX'
    #     }
    # )
    #
    # print(response)

    response = table.query(
        KeyConditionExpression=Key('artist_id').eq('00FQb4jTyendYWaN8pK0wa'),
        FilterExpression=Attr('popularity').gt(71)
    )

    # response = table.scan(
    #     FilterExpression=Attr('popularity').gt(73)
    # )
    print(response['Items'])
    print(len(response['Items']))



if __name__=='__main__':

    main()
