
import requests
r =requests.get('https://www.cryptobox.nl', verify="ca.cert")
print r.text
