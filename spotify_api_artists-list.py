import sys
import requests
import base64
import json
import logging
import pymysql
import csv

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


    # artists = []
    # with open('artist_list.csv', 'rt', encoding='UTF8') as f:
    #     raw = csv.reader(f)
    #     for row in raw:
    #         artists.append(row[0])
    #
    # for a in artists:
    #
    #     params = {
    #         "q": a,
    #         "type": "artist",
    #         "limit": "1"
    #     }
    #
    #     r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    #     raw = json.loads(r.text)

    #     artist = {}
    #
    #     try:
    #         if raw['artists']['items'][0]['name'] == params['q']:
    #             artist.update(
    #                 {
    #                     'id': raw['artists']['items'][0]['id'],
    #                     'name': raw['artists']['items'][0]['name'],
    #                     'followers': raw['artists']['items'][0]['followers']['total'],
    #                     'popularity': raw['artists']['items'][0]['popularity'],
    #                     'url': raw['artists']['items'][0]['external_urls']['spotify'],
    #                     'image_url': raw['artists']['items'][0]['images'][0]['url']
    #                 }
    #             )
    #             insert_row(cursor, artist, 'artists')
    #
    #     except:
    #         logging.error('NO ITEMS FROM SEARCH API')
    #         continue
    #
    #
    #
    #
    # conn.commit()

    cursor.execute("SELECT id FROM artists")
    artists = []

    for (id, ) in cursor.fetchall():
        artists.append(id)

    artist_batch = [artists[i: i+50] for i in range(0, len(artists), 50)]

    artist_genres = []

    for i in artist_batch:
        ids = ','.join(i)
        URL = "https://api.spotify.com/v1/artists/?ids={}".format(ids)

        r = requests.get(URL, headers=headers)
        raw = json.loads(r.text)

        for artist in raw['artists']:

            for genre in artist['genres']:

                artist_genres.append(
                    {
                        'artist_id': artist['id'],
                        'genre': genre
                    }
                )

    for data in artist_genres:
        insert_row(cursor, data, 'artist_genres')

    conn.commit()
    sys.exit(0)


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



    albums = []
    albums.extend(raw['items'])

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

    access_token = json.loads(r.text)['access_token']

    headers = {
        "Authorization": "Bearer {}".format(access_token)
    }

    return headers

def insert_row(cursor, data, table):

    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())
    key_placeholders = ', '.join(['{0}=%s'.format(k) for k in data.keys()])
    sql = "INSERT INTO %s ( %s ) VALUES ( %s ) ON DUPLICATE KEY UPDATE %s" % (table, columns,
    placeholders, key_placeholders)
    cursor.execute(sql, list(data.values())*2)



if __name__ == '__main__':
    main()
