import requests

url_wh = "https://discord.com/api/webhooks/1231251899680952380/i2N0SvUkz4xMxUMD3f5bzmi0u8OfYwFv-FG6kgWwvJDKkMKYGM43TVdBLNKCY5PUR7E6"

payload = {'content':'Des nouveaux matchs sont disponibles au pronostics sur LolProno'}
response = requests.post(url_wh, json=payload)

