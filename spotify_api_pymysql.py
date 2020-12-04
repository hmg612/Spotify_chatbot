import sys
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
        conn = pymysql.connect(host, user=username, password=password,
        db=database, port=port, use_unicode=True, charset='utf8')
        cursor = conn.cursor()

    except:
        logging.error("could not connect to RDS")
        sys.exit(1)

    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())

    print("success")
    sys.exit(0)

    headers = get_headers(client_id, client_secret)

    params = {
        "q": "BTS",
        "type": "artist",
        "limit": "5"
    }

    r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)

    try:
        r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    except:
        logging.error(r.text)
        sys.exit(1)


    r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)

    if r.status_code != 200:
        logging.error(r.text)

        if r.status_code == 429:

            retry_after = json.loads(r.headers)['Retry_After']
            time.sleep(int(retry_after))

            r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)

        ## access_token expired
        elif r.status_code == 401:

            headers = get_headers(client_id, client_secret)
            r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)

        else:
            sys.exit(1)


    # Get BTS's albums
    r = requests.get("https://api.spotify.com/v1/artists/3Nrfpe0tUJi4K4DXYWgMUX/albums", headers=headers)

    raw = json.loads(r.text)

    total = raw['total']
    offset = raw['offset']
    limit = raw['limit']
    next = raw['next']

    # print(total)
    # print(offset)
    # print(limit)
    # print(next)

    albums = []
    albums.extend(raw['items'])
    # print(len(albums))
    # sys.exit(0)

    # searching 100 contents
    count = 0
    while next:

        r = requests.get(raw['next'], headers=headers)
        raw = json.loads(r.text)
        next = raw['next']
        print(next)

        albums.extend(raw['items'])
        count = len(albums)

    print(len(albums))




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
    # print(r.text)
    # print(r.status_code)
    # print(r.headers)
    # sys.exit(0)

    access_token = json.loads(r.text)['access_token']

    headers = {
        "Authorization": "Bearer {}".format(access_token)
    }

    return headers



if __name__ == '__main__':
    main()
