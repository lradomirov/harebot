import base64
import datetime
import json
import logging
import re
import string
import random
from time import sleep

from Cryptodome.Cipher import PKCS1_v1_5
from Cryptodome.PublicKey import RSA
from bs4 import BeautifulSoup
from requests import Session, cookies
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

from model.profile import Profile


class BestBuy:
    _order_data_regex = re.compile("{}(.*){}".format(re.escape("var orderData = {"), re.escape("};")))

    _default_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    }

    _base_url = "https://www.bestbuy.com"
    _basket_count_url = _base_url + "/basket/v1/basketCount"
    _add_to_cart_url = _base_url + "/cart/api/v1/addToCart"
    _fulfillment_url = _base_url + "/checkout/r/fulfillment"
    _public_key_url = _base_url + "/api/csiservice/v2/key/tas"

    FORMAT = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    def __init__(self, product_urls: list, profile: Profile):
        self._skus = self._get_skus_from_url(product_urls)
        self._checkout_profile = profile

        self._http_session = Session()
        self._http_session.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
        self._http_session.headers['X-CLIENT-ID'] = "browse"
        # fetch cookies using selenium and apply to HTTP Session
        # BestBuy has some sort of cookie validation endpoint that is embedded in a JS file
        self._driver = webdriver.Chrome(ChromeDriverManager().install())
        self._driver.get(self._base_url)
        for cookie in self._driver.get_cookies():
            a_cookie = cookies.create_cookie(domain=cookie["domain"], name=cookie["name"], value=cookie["value"])
            self._http_session.cookies.set_cookie(a_cookie)
        self._driver.close()

    def get_item(self):
        sku_id = self._in_stock()
        if sku_id:
            self._checkout(sku_id=sku_id)

    def _get_skus_from_url(self, product_urls: list) -> string:
        return ",".join([self._get_sku_from_url(product_url) for product_url in product_urls])

    def _get_sku_from_url(self, product_url: string) -> string:
        url_len = len(product_url)
        start, stop = url_len - 7, url_len
        return product_url[start:stop]

    def _get_order_data(self) -> dict:
        r = self._http_session.get(self._fulfillment_url)

        order_data_html = BeautifulSoup(r.text, "lxml").html.head.find_all('script')[5].string
        order_data_json = json.loads("{" + self._order_data_regex.findall(order_data_html)[0] + "}")

        return {
            "orderId": order_data_json['id'],
            "customerOrderId": order_data_json['customerOrderId'],
            "itemId": order_data_json['items'][0]['id'],
            "shippingLevelOfService": order_data_json['items'][0]['meta']['fulfillments']['shipping']['availableLevelsOfService'][0]['level'],
            "paymentId": order_data_json['payment']['id']
        }

    def _get_encrypted_card_number(self, card_number: string) -> string:
        pk_json = self._http_session.get(self._public_key_url, headers=self._default_headers).json()
        rsa_pk = RSA.importKey(pk_json['publicKey'])
        cipher = PKCS1_v1_5.new(rsa_pk)
        cipher_text = cipher.encrypt(card_number.encode())
        encrypted_card_number = str(base64.b64encode(cipher_text), "utf-8") + ":".join([":3", pk_json['keyId'], self._get_obfuscated_card_number(card_number=card_number)])
        return encrypted_card_number

    def _get_obfuscated_card_number(self, card_number: string) -> string:
        repeat = len(card_number) - 10
        bin_length = 6
        last_four = -4
        return card_number[:bin_length] + ("0" * repeat) + card_number[last_four:]

    def _in_stock(self) -> string:
        logging.info(f"Looking for first available item: {self._skus}")

        next_date_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
        while True:
            try:
                r = self._http_session.get("https://www.bestbuy.com/api/3.0/priceBlocks?skus=" + self._skus)
            except ConnectionResetError as e:
                logging.error(e)
                continue

            if r.status_code == 200:

                if next_date_time < datetime.datetime.now():
                    logging.info("%s %s %s", r.status_code, r.request.method, r.request.url)
                    next_date_time = datetime.datetime.now() + datetime.timedelta(minutes=1)

                products = r.json()
                for product in products:
                    try:
                        button_state = product['sku']['buttonState']
                        purchasable = button_state['purchasable']
                    except KeyError:
                        continue
                    if purchasable:
                        logging.info(button_state['skuId'] + " is in stock!")
                        return button_state['skuId']
                sleep(random.random())
            else:
                logging.error("Request to BestBuy failed: status_code=" + str(r.status_code) + "\nreason=" + r.reason + "\ntext=" + r.text)

    def _checkout(self, sku_id: string):
        logging.info("Attempting to checkout item sku=" + sku_id)
        json_body = {"items": [{"skuId": sku_id}]}

        in_cart = False
        while not in_cart:
            r = self._http_session.post(self._add_to_cart_url, headers=self._default_headers, json=json_body)
            in_cart = r.json()['cartCount'] != 0
            sleep(0.25)

        order_data = self._get_order_data()

        checkout_url = "https://www.bestbuy.com/checkout/orders/" + order_data['orderId']
        item_update_url = checkout_url + "/items/" + order_data['itemId']

        json_body = {
            "selectedFulfillment": {
                "shipping": {
                    "address": {
                        "levelOfService": order_data['shippingLevelOfService']
                    }
                }
            }
        }
        self._http_session.patch(item_update_url, headers=self._default_headers, json=json_body)

        json_body = {
            "items": [
                {
                    "id": order_data['itemId'],
                    "type": "DEFAULT",
                    "selectedFulfillment": {
                        "shipping": {
                            "address": {
                                "firstName": self._checkout_profile.first_name,
                                "middleInitial": "",
                                "lastName": self._checkout_profile.last_name,
                                "street": self._checkout_profile.shipping_address.address_line_1,
                                "street2": self._checkout_profile.shipping_address.address_line_2,
                                "city": self._checkout_profile.shipping_address.city,
                                "state": self._checkout_profile.shipping_address.state,
                                "zipcode": self._checkout_profile.shipping_address.zipcode,
                                "country": self._checkout_profile.shipping_address.country,
                                "saveToProfile": False,
                                "useAddressAsBilling": True,
                                "override": True,
                                "isWishListAddress": False,
                                "dayPhoneNumber": self._checkout_profile.phone,
                                "type": "UNKNOWN"
                            }
                        }
                    },
                    "giftMessageSelected": False
                }
            ],
            "phoneNumber": self._checkout_profile.phone,
            "smsNotifyNumber": "",
            "smsOptIn": False,
            "emailAddress": self._checkout_profile.email
        }
        self._http_session.patch(checkout_url, headers=self._default_headers, json=json_body)
        self._http_session.post("https://www.bestbuy.com/checkout/orders/" + order_data['orderId'] + "/validate", headers=self._default_headers)

        json_body = {
            "billingAddress": {
                "firstName": self._checkout_profile.credit_card.card_holder_first_name,
                "middleInitial": "",
                "lastName": self._checkout_profile.credit_card.card_holder_last_name,
                "addressLine1": self._checkout_profile.billing_address.address_line_1,
                "addressLine2": self._checkout_profile.billing_address.address_line_2,
                "city": self._checkout_profile.billing_address.city,
                "state": self._checkout_profile.billing_address.state,
                "postalCode": self._checkout_profile.billing_address.zipcode,
                "country": self._checkout_profile.billing_address.country,
                "dayPhone": self._checkout_profile.phone,
                "useAddressAsBilling": False,
                "patchError": False,
                "isWishListAddress": False,
                "standardized": False,
                "userOverridden": True
            },
            "creditCard": {
                "hasCID": False,
                "invalidCard": False,
                "isCustomerCard": False,
                "isNewCard": True,
                "isVisaCheckout": False,
                "govPurchaseCard": False,
                "isPWPRegistered": False,
                "saveToProfile": False,
                "international": False,
                "virtualCard": False,
                "type": self._checkout_profile.credit_card.card_type,
                "number": self._get_encrypted_card_number(self._checkout_profile.credit_card.card_number),
                "binNumber": self._checkout_profile.credit_card.card_number[:6],
                "expMonth": self._checkout_profile.credit_card.expiration_month,
                "expYear": self._checkout_profile.credit_card.expiration_year,
                "cvv": self._checkout_profile.credit_card.cvv,
                "orderId": order_data['customerOrderId']
            }
        }
        logging.info(json_body)
        payment_headers = self._default_headers
        payment_headers['X-CLIENT'] = "CHECKOUT"
        payment_headers['X-CONTENT-ID'] = order_data['customerOrderId']
        self._http_session.put("https://www.bestbuy.com/payment/api/v1/payment/" + order_data['paymentId'] + "/creditCard", headers=payment_headers, json=json_body)

        self._http_session.post("https://www.bestbuy.com/checkout/orders/" + order_data['orderId'] + "/paymentMethods/refreshPayment", headers=payment_headers)

        payment_headers['UT'] = "undefined"
        payment_headers['VT'] = self._http_session.cookies.get("VT")
        json_body = {"orderId": order_data['customerOrderId'],
                     "browserInfo": {"javaEnabled": False, "language": "en-US", "userAgent": self._http_session.headers["User-Agent"], "height": "1080", "width": "1080", "timeZone": "300",
                                     "colorDepth": "24"}}
        r = self._http_session.post("https://www.bestbuy.com/payment/api/v1/payment/" + order_data['paymentId'] + "/threeDSecure/preLookup", headers=payment_headers, json=json_body).json()

        three_ds_reference_id = r['threeDSReferenceId']
        json_body = {"orderId": order_data['orderId'], "threeDSecureStatus": {"threeDSReferenceId": three_ds_reference_id}}
        r = self._http_session.post("https://www.bestbuy.com/checkout/api/1.0/paysecure/submitCardAuthentication", headers=payment_headers, json=json_body)

        json_body = {"browserInfo": {"javaEnabled": False, "language": "en-US", "userAgent": self._http_session.headers["User-Agent"], "height": "1080", "width": "1080", "timeZone": "300", "colorDepth": "24"}}
        r = self._http_session.post("https://www.bestbuy.com/checkout/orders/" + order_data['orderId'], headers=payment_headers, json=json_body)

        if r.status_code != 200:
            logging.error(r.text)
            logging.error(r.json())

        r = self._http_session.get(self._basket_count_url)
        print(r.status_code, r.text, sep=",")
        logging.info("Successfully checked out!  Check your email for order information.")

