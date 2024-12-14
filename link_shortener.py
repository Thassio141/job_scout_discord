import requests

def shorten_url_tinyurl_api(long_url):
    api_url = f"https://tinyurl.com/api-create.php?url={long_url}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.text
    else:
        return f"Erro: {response.status_code}, {response.text}"