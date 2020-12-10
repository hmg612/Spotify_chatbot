import sys
import os
import boto3
import requests
import base64
import json
import logging
import pymysql

client_id = "78f2ea1df4634e4fbd54bbb001bc15f7"
client_secret = "075cf8c8b5d947bfa3e334a450b18bbe"

host = "data-engineering-spotify.cqbikpgdcu2y.ap-northeast-2.rds.amazonaws.com"
port = 3306
username = "admin"
database = "production"
password = "admin1234"

def main():

    try:
        dynamodb = boto3.resource('dynamodb', region_name='ap-northeast-2',
        endpoint_url='http://dynamodb.ap-northeast-2.amazonaws.com')
    except:
        logging.error('could not connect to dynamodb')
        sys.exit(1)

    try:
        conn = pymysql.connect(host, user=username, password=password,
        db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()

    except:
        logging.error("could not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id, client_secret)

    table = dynamodb.Table('top_tracks')

    cursor.execute('SELECT id FROM artists')

    for (artist_id, ) in cursor.fetchall():
        URL = "https://api.spotify.com/v1/artists/{}/top-tracks".format(artist_id)
        params = {
            'country': 'US'
        }

        r = requests.get(URL, params=params, headers=headers)
        raw = json.loads(r.text)

        for track in raw['tracks']:
            data = {
                'artist_id': artist_id
            }

            data.update(track)

            table.put_item(
                Item=data
            )



def get_headers(client_id, client_secret):

    endpoint = "https://accounts.spotify.com/api/token"
    encoded = base64.b64encode("{}:{}".format(client_id, client_secret).encode('utf-8')).decode('ascii')

    headers = {
        "Authorization": "Basic {}".format(encoded)
    }

    payload = {
        "grant_type": "client_credentials"
    }

    r = requests.post(endpoint, data=payload, headers=headers)

    access_token = json.loads(r.text)['access_token']

    headers = {
        "Authorization": "Bearer {}".format(access_token)
    }

    return headers



if __name__=='__main__':

    main()
