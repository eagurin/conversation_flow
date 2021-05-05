import json
import os
import sys

import requests
from dotenv import load_dotenv

sys.path.append("..")
load_dotenv()


access_token = os.getenv("POST_API_ACCESS_TOKEN")
login_password = os.getenv("POST_API_LOGIN_PASSWORD")
protocol = "https://"
host = "otpravka-api.pochta.ru"


class Post:
    recognize_address = ''
    method = None
    city = None
    street = None
    house = None
    index = None
    delivery_time = None

    def request_headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json;charset=UTF-8",
            "Authorization": "AccessToken " + access_token,
            "X-User-Authorization": "Basic " + login_password,
        }

    def set_on_address(self, recognize_address):
        self.recognize_address += recognize_address + ' '

    def set_on_method(self, method):
        self.method = method

    def set_on_city(self, city):
        self.city = city

    def do_clear_address(self):
        path = "/1.0/clean/address"
        url = protocol + host + path
        data = {"id": "adr 1"}
        if self.city:
            data.update({'place': 'г ' + self.city})
        if self.house:
            data.update({'house': str(self.house)})
        if self.index:
            data.update({"index": str(self.index)})
        data.update({"original-address": self.recognize_address + ' г ' + self.city + ' дом ' + str(self.house) + ' индекс ' + str(self.index)})
        try:
            response = requests.post(url, headers=self.request_headers(), data=json.dumps([data]))
            self.address = json.loads(response.text)
            print("\nStatus code: ", response.status_code)
            print("Response body: ", response.text)
            if 'street' in response.text:
                self.street = self.address[0]["street"]
            if 'house' in response.text:
                self.house = self.address[0]["house"]
            if 'region' in response.text:
                self.region = self.address[0]["region"]
            if 'index' in response.text:
                self.index = self.address[0]["index"]
                print('\nIndex: ', self.index)
        except:
            raise

    def get_delivery_cost(self):
        path = "/1.0/tariff"
        url = protocol + host + path
        destination = {
            "index-from": "603167",
            "index-to": self.index,
            "mail-category": "ORDINARY",
            "mail-type": self.method,
            "mass": 300,
            "fragile": "false",
            "dimension": {"height": 15, "length": 10, "width": 18},
        }
        try:
            response = requests.post(url, headers=self.request_headers(), data=json.dumps(destination))
            pre = json.loads(response.text)
            print("\nStatus code: ", response.status_code)
            print("Response body: ", response.text)
            self.cost = ((pre["total-rate"] + pre["total-vat"]) // 100) + 80
            self.delivery_time = pre['delivery-time']['max-days'] or None
            self.recognize_address = ''
            self.street = None
            self.house = None
            self.index = None
        except:
            raise

    def getindex(self):
        self.get_clear_address()
        return self.index
