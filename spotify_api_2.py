import sys
import requests
import base64
import json
import logging

client_id = "78f2ea1df4634e4fbd54bbb001bc15f7"
client_secret = "075cf8c8b5d947bfa3e334a450b18bbe"

def main():

    headers = get_headers(client_id, client_secret)
    # print(headers)
    # sys.exit(0)

    params = {
        "q": "BTS",
        "type": "artist",
        "limit": "5"
    }

    r = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers)
    print(r.status_code)
    print(r.text)
    sys.exit(0)



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



if __name__ == '__main__':
    main()
