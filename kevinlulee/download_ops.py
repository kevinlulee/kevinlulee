import os
import requests
import kevinlulee as kx

def download_image(url, filename=None, directory='~/data/images/trash/'):
    directory = os.path.expanduser(directory)
    if not filename:
        filename = os.path.basename(url)
    
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    response = requests.get(url, stream=True)
    if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
        with open(path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return path
    else:
        raise ValueError('URL did not return an image.')

# url = 'https://i.redd.it/9t0ecsdnj3ef1.jpeg'
# print(download_image(url))

def fetch(url):
    BROWSER_AGENT = "Mozilla/5.0 (X11; CrOS aarch64 13310.93.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.133 Safari/537.36"
    r = requests.get(url, {"user-agent": BROWSER_AGENT})
    if r.status_code == 200:
        try:
            return kx.json.loads(r.text)
        except Exception as e:
            return r.text



def get_archive_org_text_document(url, query = 'pre'):
    url = 'https://archive.org/stream/WalkTwoMoons/twomoon_djvu.txt'
    from bs4 import BeautifulSoup
    from kevinlulee.download_ops import fetch
    html = fetch(url)

    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.select(query)
    for element in elements:
        return element.text
