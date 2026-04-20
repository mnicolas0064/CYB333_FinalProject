import requests

url = 'https://catalog.s.download.windowsupdate.com/microsoftupdate/v6/wsusscan/wsusscn2.cab'
response = requests.get(url)

if response.status_code == 200:
    with open('wsusscn2.cab', 'wb') as f:
        f.write(response.content)