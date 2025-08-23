import requests
import json

url = "https://ship-test.envia.com/ship/rate/"

payload = json.dumps(
    {
        "origin": {
            "name": "USA",
            "company": "enviacommarcelo",
            "email": "juanpedrovazez@hotmail.com",
            "phone": "8182000536",
            "street": "351523",
            "number": "crescent ave",
            "district": "other",
            "city": "dallas",
            "state": "tx",
            "country": "US",
            "postalCode": "75205",
            "reference": "",
            "coordinates": {"latitude": "32.776272", "longitude": "-96.796856"},
        },
        "destination": {
            "name": "francisco",
            "company": "",
            "email": "",
            "phone": "8180180543",
            "street": "4th street",
            "number": "24",
            "district": "other",
            "city": "reno",
            "state": "nv",
            "country": "US",
            "postalCode": "89503",
            "reference": "",
            "coordinates": {"latitude": "39.512132", "longitude": "-119.906585"},
        },
        "packages": [
            {
                "content": "zapatos",
                "amount": 1,
                "type": "box",
                "weight": 1,
                "insurance": 0,
                "declaredValue": 0,
                "weightUnit": "LB",
                "lengthUnit": "IN",
                "dimensions": {"length": 11, "width": 15, "height": 20},
            }
        ],
        "shipment": {"carrier": "usps", "type": 1},
        "settings": {"currency": "USD"},
    }
)
headers = {"Content-Type": "application/json", "Authorization": "Bearer b2657f78d29c317f9031dfc2266845de8e11e30bf7877f1cdf9fb9d47cde150b"}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
