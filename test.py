import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

url = "https://hrd.work24.go.kr/hrdp/co/pcobo/PCOBO0107TAjax.do"

params = {
    "tracseId": "AIG20240000492539",
    "tracseTme": "2",
    "trainstCstmrId": "500037933544",
}


headers = {
    "Referer": "https://hrd.work24.go.kr/hrdp/co/pcobo/PCOBO0100P.do?tracseId=AIG20240000492539&tracseTme=2&crseTracseSe=C0061&trainstCstmrId=500037933544",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

response = requests.get(url, params=params, headers=headers)

soup = BeautifulSoup(response.text, "html.parser")

print(soup.find_all("dl", class_="item"))
