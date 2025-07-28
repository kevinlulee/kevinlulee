import requests
def has_internet():
    try:
        response = requests.get("https://www.google.com", timeout=1)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

