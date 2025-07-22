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
