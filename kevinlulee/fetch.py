import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from kevinlulee.file_utils import writefile

def fetch(url, **kwargs):
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            return response.json()
        return response.text

    except ConnectionError as e:
        raise e
    except Exception as e:
        print(e)
        return 



url = 'https://raw.githubusercontent.com/tree-sitter/tree-sitter-pythont/master/tree/src/node-types.json'
url = 'https://raw.githubusercontent.com/uben0/tree-sitter-typst/refs/heads/master/typescript/src/node-types.json'
url = 'https://raw.githubusercontent.com/uben0/tree-sitter-typst/refs/heads/master/src/node-types.json'
writefile('/home/kdog3682/projects/python/codeform/typst-node-types.json', fetch(url))
