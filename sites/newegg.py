import logging
import time

import requests

rtx_3080_product_numbers = [
    "14-137-597",
    "14-137-600",
    "14-126-457",
    "14-137-609",
    "14-932-337",
    "14-932-336",
    "14-487-520",
    "14-126-452",
    "14-126-453",
    "14-137-598",
    "14-932-330",
    "14-932-367",
    "14-487-522"
]


class Newegg:
    rtx_3080_product_numbers = []

    def __init__(self, product_numbers):
        self.product_numbers = product_numbers

    def get_video_card(self):
        logging.basicConfig(level=logging.INFO)
        s = requests.Session()
        s.headers["User-Agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:83.0) Gecko/20100101 Firefox/83.0"

        while True:
            time.sleep(5)

            for product_number in self.product_numbers:
                time.sleep(2)
                url = f"https://www.newegg.com/product/api/ProductRealtime?ItemNumber={product_number}"
                r = s.get(url)
                logging.info(f"{r.status_code}, {url}")
                if r:
                    logging.info(r.json())
                    in_stock = r.json()["MainItem"]["Instock"]
                    if in_stock:
                        logging.info("is in stock!" + url)
                else:
                    logging.warning(f"request failed to newegg.com\n{url}")
                    break


if __name__ in "__main__":
    newegg = Newegg(rtx_3080_product_numbers)
    newegg.get_video_card()
