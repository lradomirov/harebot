import logging
import string
import time
from enum import Enum

from bs4 import BeautifulSoup
from requests import Session

from sites import SupremeCheckout


class SupremeSizes(Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    EXTRA_LARGE = "XLarge"


class Supreme:
    logging.basicConfig(level=logging.INFO)

    def checkout(self, http_session: Session, checkout: SupremeCheckout):
        checkout_url = "https://www.supremenewyork.com/checkout"
        r = http_session.get(checkout_url)
        soup = BeautifulSoup(r.text, 'lxml')
        data = {
            "Content-Type": "text/html; charset=UTF-8",
            "utf8": "",
            "authenticity_token": "",
            "current_time": "",
            "cerear": "RMCEAR",
            "g-recaptcha-response": "",
            "order[email]": checkout.email,
            "order[tel]": checkout.phone,
            "order[billing_name]": checkout.name,
            "order[billing_address]": checkout.address_line_1,
            "order[billing_address_2]": checkout.address_line_2,
            "order[billing_city]": checkout.city,
            "order[billing_state]": checkout.state,
            "order[billing_zip]": checkout.zipcode,
            "order[billing_country]": checkout.country,
            "order[terms]": [
                "0",
                "1"
            ],
            "same_as_billing": "1",
            "store_credit_id": "",
            "riearmxa": checkout.card_number,
            "credit_card[type]": "credit card",
            "credit_card[month]": checkout.expiration_month,
            "credit_card[year]": checkout.expiration_year,
            "credit_card[meknk]": checkout.card_cvv,
            "credit_card[vval]": ""
        }

        if soup:
            select_item_form = soup.body.form
            input_elements = ["utf8", "authenticity_token", "current_time", "cerear"]

            for input_element in select_item_form.find_all(attrs={"name": input_elements}):
                data[input_element['name']] = input_element['value']

            r = http_session.post(checkout_url + ".json", data=data)
            logging.info(f"data: {data}")
            logging.info(f"status: {r.status_code}")
            logging.info(f"response: {r.json()}")

    def add_to_cart(self, url: string, size: SupremeSizes) -> Session:
        http_session = Session()
        http_session.headers["User-Agent"] = \
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0"
        r = http_session.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        input_elements = ["utf8", "authenticity_token", "h", "st"]

        if soup:
            data = {}
            select_item_form = soup.body.form
            add_to_cart_endpoint = "https://www.supremenewyork.com" + select_item_form['action']

            for input_element in select_item_form.find_all(attrs={"name": input_elements}):
                data[input_element['name']] = input_element['value']

            if size:
                size_elements = select_item_form.fieldset.find_all("option")
                for size_element in size_elements:
                    if size_element.string == size.value:
                        data['s'] = size_element['value']
                        break

            r = http_session.post(add_to_cart_endpoint, data=data)
            logging.info(f"status: {r.status_code}")
            logging.info(f"response: {r.json()}")
            return http_session


if __name__ in "__main__":
    checkout = SupremeCheckout('f f', "f@f.com", "123-123-1231", "f", "f", "f", "OH", "44125", "USA",
                               "123123123123123", "12", "2022", "213")
    for x in range(20):
        tic = time.perf_counter()
        supreme = Supreme()
        session = supreme.add_to_cart("https://www.supremenewyork.com/shop/jackets/akgs1vbcr", SupremeSizes.MEDIUM)
        if session:
            supreme.checkout(session, checkout=checkout)
