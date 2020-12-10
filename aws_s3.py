import sys
import os
import boto3
import requests
import base64
import json
import logging
import pymysql
from datetime import datetime
import pandas as pd
import jsonpath

client_id = "78f2ea1df4634e4fbd54bbb001bc15f7"
client_secret = "075cf8c8b5d947bfa3e334a450b18bbe"

host = "data-engineering-spotify.cqbikpgdcu2y.ap-northeast-2.rds.amazonaws.com"
port = 3306
username = "admin"
database = "production"
password = "admin1234"

def main():

    try:
        conn = pymysql.connect(host, user=username, password=password,
        db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()

    except:
        logging.error("could not connect to RDS")
        sys.exit(1)

    headers = get_headers(client_id, client_secret)

    # RDS - 아티스트ID 가져오기
    cursor.execute("SELECT id FROM artists LIMIT 10")

    top_track_keys = {
        "id": "id",
        "name": "name",
        "popularity": "popularity",
        "external_url": "external_urls.spotify"
    }
    # Top tracks 가져오기
    top_tracks = []
    for (id, ) in cursor.fetchall():
        URL = "https://api.spotify.com/v1/artists/{}/top-tracks".format(id)
        params = {
            'country': 'US'
        }

        r = requests.get(URL, params=params, headers=headers)
        raw = json.loads(r.text)

        for i in raw['tracks']:
            top_track = {}
            for k, v in top_track_keys.items():
                top_track.update({k: jsonpath.jsonpath(i, v)})
                top_track.update({'artist_id': id})
                top_tracks.append(top_track)

    #json 형식을 parquet화 하기(Spark에서 더 유용하게 사용할 수 있는 데이터형식)
    top_tracks = pd.DataFrame(raw)
    top_tracks.to_parquet('top-tracks.parquet', engine='pyarrow', compression='snappy')

    sys.exit(0)
    dt = datetime.utcnow().strftime("%Y-%m-%d")
    # with open('top_tracks.json', 'w') as f:
    #     for i in top_tracks:
    #         json.dump(i, f)
    #         f.write(os.linesep)

    s3 = boto3.resource('s3')
    object = s3.Object('spotify-artist', 'dt={}/top-tracks.json'.format(dt))
    data = open('top-tracks.parquet', 'rb')
    object.put(Body=data)


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
